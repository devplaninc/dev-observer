import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from github import Auth, Github
from github.Repository import Repository as GithubRepository
from github.Commit import Commit
from github.PullRequest import PullRequest
from github.Issue import Issue

from dev_observer.api.types.changes_pb2 import (
    GitHubChangesSummary, ChangesSummaryContent, CommitInfo, FileChange,
    PullRequestInfo, IssueInfo, ChangesStatistics, LanguageStats,
    ChangeType, ChangesSummaryStatus
)
from dev_observer.api.types.repo_pb2 import GitHubRepository as RepoProto
from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.log import s_
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.repository.auth.github_app import GithubAppAuthProvider
from dev_observer.repository.auth.github_token import GithubTokenAuthProvider
from dev_observer.repository.types import ObservedRepo
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class ChangesSummaryProcessor:
    _storage: StorageProvider
    _analysis: AnalysisProvider
    _prompts: PromptsProvider
    _clock: Clock
    _github_auth: GithubAppAuthProvider | GithubTokenAuthProvider

    def __init__(
        self,
        storage: StorageProvider,
        analysis: AnalysisProvider,
        prompts: PromptsProvider,
        github_auth: GithubAppAuthProvider | GithubTokenAuthProvider,
        clock: Clock = RealClock(),
    ):
        self._storage = storage
        self._analysis = analysis
        self._prompts = prompts
        self._clock = clock
        self._github_auth = github_auth

    async def create_changes_summary(
        self, 
        repo: RepoProto, 
        days_back: int = 7
    ) -> GitHubChangesSummary:
        """Create a new changes summary for a repository"""
        summary_id = str(uuid.uuid4())
        end_date = self._clock.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Create initial summary with pending status
        summary = GitHubChangesSummary(
            id=summary_id,
            repo_id=repo.id,
            repo_full_name=repo.full_name,
            created_at=end_date,
            analysis_period_start=start_date,
            analysis_period_end=end_date,
            status=ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_PENDING
        )
        
        # Save to storage
        await self._storage.save_changes_summary(summary)
        
        # Process asynchronously
        await self._process_changes_summary(summary)
        
        return summary

    async def _process_changes_summary(self, summary: GitHubChangesSummary):
        """Process the changes summary asynchronously"""
        try:
            # Update status to processing
            summary.status = ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_PROCESSING
            await self._storage.save_changes_summary(summary)
            
            # Get repository data
            repo = await self._storage.get_github_repo(summary.repo_id)
            if not repo:
                raise ValueError(f"Repository {summary.repo_id} not found")
            
            observed_repo = ObservedRepo(url=repo.url, github_repo=repo)
            
            # Fetch GitHub data
            content = await self._fetch_github_data(observed_repo, summary)
            
            # Generate AI summary
            ai_summary = await self._generate_ai_summary(content, observed_repo)
            content.summary = ai_summary
            
            # Update summary
            summary.content.CopyFrom(content)
            summary.status = ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_COMPLETED
            
            await self._storage.save_changes_summary(summary)
            
        except Exception as e:
            _log.error(s_("Failed to process changes summary", summary_id=summary.id), exc_info=e)
            summary.status = ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_FAILED
            summary.error_message = str(e)
            await self._storage.save_changes_summary(summary)

    async def _fetch_github_data(
        self, 
        repo: ObservedRepo, 
        summary: GitHubChangesSummary
    ) -> ChangesSummaryContent:
        """Fetch GitHub data for the analysis period"""
        auth = await self._github_auth.get_auth(repo)
        
        with Github(auth=auth) as gh:
            github_repo = gh.get_repo(repo.github_repo.full_name)
            
            # Fetch commits
            commits = await self._fetch_commits(github_repo, summary)
            
            # Fetch pull requests
            pull_requests = await self._fetch_pull_requests(github_repo, summary)
            
            # Fetch issues
            issues = await self._fetch_issues(github_repo, summary)
            
            # Analyze file changes
            file_changes = await self._analyze_file_changes(commits)
            
            # Calculate statistics
            statistics = await self._calculate_statistics(
                commits, file_changes, pull_requests, issues
            )
            
            return ChangesSummaryContent(
                commits=commits,
                file_changes=file_changes,
                pull_requests=pull_requests,
                issues=issues,
                statistics=statistics
            )

    async def _fetch_commits(
        self, 
        github_repo: GithubRepository, 
        summary: GitHubChangesSummary
    ) -> List[CommitInfo]:
        """Fetch commits for the analysis period"""
        commits = []
        since = summary.analysis_period_start
        until = summary.analysis_period_end
        
        try:
            for commit in github_repo.get_commits(since=since, until=until):
                commit_info = CommitInfo(
                    sha=commit.sha,
                    message=commit.commit.message,
                    author=commit.commit.author.name,
                    committed_at=commit.commit.author.date,
                    additions=commit.stats.additions if commit.stats else 0,
                    deletions=commit.stats.deletions if commit.stats else 0
                )
                
                # Get files changed
                if commit.files:
                    commit_info.files_changed.extend([f.filename for f in commit.files])
                
                commits.append(commit_info)
                
        except Exception as e:
            _log.error(s_("Failed to fetch commits", repo=github_repo.full_name), exc_info=e)
        
        return commits

    async def _fetch_pull_requests(
        self, 
        github_repo: GithubRepository, 
        summary: GitHubChangesSummary
    ) -> List[PullRequestInfo]:
        """Fetch pull requests for the analysis period"""
        pull_requests = []
        since = summary.analysis_period_start
        
        try:
            for pr in github_repo.get_pulls(state='all'):
                # Only include PRs that were updated during the analysis period
                if pr.updated_at >= since:
                    pr_info = PullRequestInfo(
                        number=pr.number,
                        title=pr.title,
                        state=pr.state,
                        author=pr.user.login if pr.user else "Unknown",
                        created_at=pr.created_at,
                        updated_at=pr.updated_at,
                        merged_at=pr.merged_at,
                        additions=pr.additions or 0,
                        deletions=pr.deletions or 0
                    )
                    
                    # Get labels
                    if pr.labels:
                        pr_info.labels.extend([label.name for label in pr.labels])
                    
                    pull_requests.append(pr_info)
                    
        except Exception as e:
            _log.error(s_("Failed to fetch pull requests", repo=github_repo.full_name), exc_info=e)
        
        return pull_requests

    async def _fetch_issues(
        self, 
        github_repo: GithubRepository, 
        summary: GitHubChangesSummary
    ) -> List[IssueInfo]:
        """Fetch issues for the analysis period"""
        issues = []
        since = summary.analysis_period_start
        
        try:
            for issue in github_repo.get_issues(state='all'):
                # Only include issues that were updated during the analysis period
                if issue.updated_at >= since:
                    issue_info = IssueInfo(
                        number=issue.number,
                        title=issue.title,
                        state=issue.state,
                        author=issue.user.login if issue.user else "Unknown",
                        created_at=issue.created_at,
                        updated_at=issue.updated_at,
                        closed_at=issue.closed_at
                    )
                    
                    # Get labels
                    if issue.labels:
                        issue_info.labels.extend([label.name for label in issue.labels])
                    
                    issues.append(issue_info)
                    
        except Exception as e:
            _log.error(s_("Failed to fetch issues", repo=github_repo.full_name), exc_info=e)
        
        return issues

    async def _analyze_file_changes(self, commits: List[CommitInfo]) -> List[FileChange]:
        """Analyze file changes from commits"""
        file_changes = {}
        
        for commit in commits:
            for file_path in commit.files_changed:
                if file_path not in file_changes:
                    file_changes[file_path] = FileChange(
                        file_path=file_path,
                        change_type=ChangeType.CHANGE_TYPE_MODIFIED,
                        additions=0,
                        deletions=0,
                        language=self._detect_language(file_path)
                    )
                
                # Add commit stats to file totals
                file_changes[file_path].additions += commit.additions
                file_changes[file_path].deletions += commit.deletions
        
        return list(file_changes.values())

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
        
        language_map = {
            'py': 'Python',
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'java': 'Java',
            'cpp': 'C++',
            'c': 'C',
            'go': 'Go',
            'rs': 'Rust',
            'php': 'PHP',
            'rb': 'Ruby',
            'swift': 'Swift',
            'kt': 'Kotlin',
            'scala': 'Scala',
            'html': 'HTML',
            'css': 'CSS',
            'scss': 'SCSS',
            'sass': 'Sass',
            'json': 'JSON',
            'yaml': 'YAML',
            'yml': 'YAML',
            'toml': 'TOML',
            'md': 'Markdown',
            'txt': 'Text',
            'sh': 'Shell',
            'bash': 'Bash',
            'sql': 'SQL',
            'xml': 'XML'
        }
        
        return language_map.get(ext, 'Unknown')

    async def _calculate_statistics(
        self,
        commits: List[CommitInfo],
        file_changes: List[FileChange],
        pull_requests: List[PullRequestInfo],
        issues: List[IssueInfo]
    ) -> ChangesStatistics:
        """Calculate statistics from the collected data"""
        # Language statistics
        language_stats = {}
        for file_change in file_changes:
            lang = file_change.language or 'Unknown'
            if lang not in language_stats:
                language_stats[lang] = LanguageStats(
                    language=lang,
                    files_changed=0,
                    additions=0,
                    deletions=0
                )
            
            language_stats[lang].files_changed += 1
            language_stats[lang].additions += file_change.additions
            language_stats[lang].deletions += file_change.deletions
        
        return ChangesStatistics(
            total_commits=len(commits),
            total_additions=sum(c.additions for c in commits),
            total_deletions=sum(c.deletions for c in commits),
            total_files_changed=len(file_changes),
            total_pull_requests=len(pull_requests),
            total_issues=len(issues),
            language_stats=list(language_stats.values())
        )

    async def _generate_ai_summary(
        self, 
        content: ChangesSummaryContent, 
        repo: ObservedRepo
    ) -> str:
        """Generate AI summary of the changes"""
        try:
            # Create a comprehensive prompt for analysis
            prompt = f"""
Analyze the recent changes in the GitHub repository {repo.github_repo.full_name}.

Repository: {repo.github_repo.full_name}
Analysis Period: {content.statistics.total_commits} commits, {content.statistics.total_pull_requests} PRs, {content.statistics.total_issues} issues

Key Statistics:
- Total commits: {content.statistics.total_commits}
- Total additions: {content.statistics.total_additions} lines
- Total deletions: {content.statistics.total_deletions} lines
- Files changed: {content.statistics.total_files_changed}
- Pull requests: {content.statistics.total_pull_requests}
- Issues: {content.statistics.total_issues}

Top Languages by changes:
{chr(10).join([f"- {lang.language}: {lang.files_changed} files, +{lang.additions}/-{lang.deletions} lines" for lang in content.statistics.language_stats[:5]])}

Recent Commits (last 10):
{chr(10).join([f"- {commit.sha[:8]}: {commit.message[:100]} by {commit.author}" for commit in content.commits[:10]])}

Recent Pull Requests:
{chr(10).join([f"- #{pr.number}: {pr.title} ({pr.state}) by {pr.author}" for pr in content.pull_requests[:5]])}

Recent Issues:
{chr(10).join([f"- #{issue.number}: {issue.title} ({issue.state}) by {issue.author}" for issue in content.issues[:5]])}

Please provide a comprehensive summary of the recent activity in this repository, including:
1. Overall development activity level
2. Key changes and improvements
3. Notable pull requests and their impact
4. Important issues and their resolution status
5. Technology stack insights based on file changes
6. Development velocity and trends

Write a clear, professional summary suitable for stakeholders and team members.
"""
            
            # Use the analysis provider to generate the summary
            result = await self._analysis.analyze(prompt)
            return result.content if result else "Unable to generate summary at this time."
            
        except Exception as e:
            _log.error(s_("Failed to generate AI summary", repo=repo.github_repo.full_name), exc_info=e)
            return f"Summary generation failed: {str(e)}" 