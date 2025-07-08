import json
import logging
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import List, Optional

from github import Github
from google.protobuf.timestamp_pb2 import Timestamp

from dev_observer.api.types.repo_pb2 import GitHubChangeSummary, GitHubChangeAnalysis
from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.repository.types import ObservedRepo
from dev_observer.repository.github import GithubAuthProvider
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class GitHubChangeAnalyzer:
    _auth_provider: GithubAuthProvider
    _storage: StorageProvider
    _analysis_provider: AnalysisProvider
    _clock: Clock

    def __init__(
        self,
        auth_provider: GithubAuthProvider,
        storage: StorageProvider,
        analysis_provider: AnalysisProvider,
        clock: Clock = RealClock(),
    ):
        self._auth_provider = auth_provider
        self._storage = storage
        self._analysis_provider = analysis_provider
        self._clock = clock

    async def analyze_recent_changes(
        self, repo: ObservedRepo, days_back: int = 7, analysis_type: str = "weekly"
    ) -> Optional[GitHubChangeSummary]:
        """Analyze recent changes in a GitHub repository."""
        try:
            full_name = repo.github_repo.full_name
            end_time = self._clock.now()
            start_time = end_time - timedelta(days=days_back)

            auth = await self._auth_provider.get_auth(repo)
            with Github(auth=auth) as gh:
                gh_repo = gh.get_repo(full_name)
                
                # Get commits from the period
                commits = list(gh_repo.get_commits(since=start_time, until=end_time))
                
                if not commits:
                    _log.info(f"No commits found for {full_name} in the last {days_back} days")
                    return None

                # Clone repository to analyze changes
                with tempfile.TemporaryDirectory() as temp_dir:
                    await self._clone_repo(repo, temp_dir)
                    
                    # Get detailed change analysis
                    change_analysis = await self._analyze_git_changes(
                        temp_dir, start_time, end_time, commits
                    )
                    
                    # Generate AI summary
                    summary_text = await self._generate_ai_summary(change_analysis)
                    
                    # Create change summary
                    change_summary = GitHubChangeSummary()
                    change_summary.repo_id = repo.github_repo.id
                    change_summary.commit_sha = commits[0].sha if commits else ""
                    change_summary.analysis_type = analysis_type
                    change_summary.summary = summary_text
                    change_summary.changes_data = json.dumps(change_analysis.__dict__)
                    
                    # Set timestamps
                    start_timestamp = Timestamp()
                    start_timestamp.FromDatetime(start_time)
                    change_summary.analysis_period_start.CopyFrom(start_timestamp)
                    
                    end_timestamp = Timestamp()
                    end_timestamp.FromDatetime(end_time)
                    change_summary.analysis_period_end.CopyFrom(end_timestamp)
                    
                    # Save to storage
                    return await self._storage.add_github_change_summary(change_summary)
                    
        except Exception as e:
            _log.error(f"Failed to analyze changes for {repo.github_repo.full_name}: {e}")
            return None

    async def _clone_repo(self, repo: ObservedRepo, dest: str):
        """Clone repository for analysis."""
        token = await self._auth_provider.get_cli_token_prefix(repo)
        clone_url = repo.github_repo.url.replace("https://", f"https://{token}@")
        
        result = subprocess.run(
            ["git", "clone", "--depth=50", clone_url, dest],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to clone repository: {result.stderr}")

    async def _analyze_git_changes(
        self, repo_path: str, start_time: datetime, end_time: datetime, commits: List
    ) -> GitHubChangeAnalysis:
        """Analyze git changes using git commands."""
        analysis = GitHubChangeAnalysis()
        
        # Get commit information
        analysis.commits.extend([commit.sha for commit in commits])
        analysis.authors.extend(list(set([commit.author.login for commit in commits if commit.author])))
        
        # Get file changes using git diff
        since_date = start_time.strftime("%Y-%m-%d")
        until_date = end_time.strftime("%Y-%m-%d")
        
        # Get changed files
        diff_result = subprocess.run(
            ["git", "diff", "--name-only", f"--since={since_date}", f"--until={until_date}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if diff_result.returncode == 0:
            files = [f.strip() for f in diff_result.stdout.split('\n') if f.strip()]
            analysis.files_changed.extend(files)
        
        # Get stats
        stat_result = subprocess.run(
            ["git", "diff", "--stat", f"--since={since_date}", f"--until={until_date}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if stat_result.returncode == 0:
            # Parse additions and deletions from git diff --stat output
            lines = stat_result.stdout.split('\n')
            for line in lines:
                if 'insertion' in line and 'deletion' in line:
                    parts = line.split(',')
                    for part in parts:
                        if 'insertion' in part:
                            analysis.total_additions = int(part.strip().split()[0])
                        elif 'deletion' in part:
                            analysis.total_deletions = int(part.strip().split()[0])
        
        # Generate key changes summary
        analysis.key_changes.extend([
            f"Modified {len(analysis.files_changed)} files",
            f"Added {analysis.total_additions} lines",
            f"Removed {analysis.total_deletions} lines",
            f"Contributors: {', '.join(analysis.authors[:5])}"
        ])
        
        return analysis

    async def _generate_ai_summary(self, change_analysis: GitHubChangeAnalysis) -> str:
        """Generate AI summary of changes."""
        prompt = f"""
        Analyze the following GitHub repository changes and provide a concise summary:
        
        Files Changed: {', '.join(change_analysis.files_changed[:10])}
        Commits: {len(change_analysis.commits)}
        Authors: {', '.join(change_analysis.authors)}
        Lines Added: {change_analysis.total_additions}
        Lines Removed: {change_analysis.total_deletions}
        
        Provide a brief, professional summary of what changes were made, focusing on:
        1. Main areas of development
        2. Key features or fixes implemented
        3. Overall impact of changes
        
        Keep the summary under 200 words.
        """
        
        try:
            response = await self._analysis_provider.analyze(
                prompt, "github_change_summary", {}
            )
            return response.get("summary", "Unable to generate summary")
        except Exception as e:
            _log.error(f"Failed to generate AI summary: {e}")
            return f"Changes include {len(change_analysis.files_changed)} files modified by {len(change_analysis.authors)} contributors with {change_analysis.total_additions} additions and {change_analysis.total_deletions} deletions."