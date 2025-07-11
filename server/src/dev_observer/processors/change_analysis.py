import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.types.repo_pb2 import RepoChangeAnalysis
from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.analytics.provider import ChangeAnalysisAnalytics
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.repository.change_analysis import GitHubRepositoryProvider
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class ChangeAnalysisProcessor:
    _storage: StorageProvider
    _github_provider: GitHubRepositoryProvider
    _analysis_provider: AnalysisProvider
    _observations_provider: ObservationsProvider
    _analytics: ChangeAnalysisAnalytics
    _clock: Clock

    def __init__(
        self,
        storage: StorageProvider,
        github_provider: GitHubRepositoryProvider,
        analysis_provider: AnalysisProvider,
        observations_provider: ObservationsProvider,
        analytics: ChangeAnalysisAnalytics,
        clock: Clock = RealClock(),
    ):
        self._storage = storage
        self._github_provider = github_provider
        self._analysis_provider = analysis_provider
        self._observations_provider = observations_provider
        self._analytics = analytics
        self._clock = clock

    async def run_daily_analysis(self):
        _log.info("Starting daily change analysis for all enrolled repositories")
        
        try:
            enrolled_repos = await self._storage.get_enrolled_repos_for_change_analysis()
            _log.info(s_("Found enrolled repositories", count=len(enrolled_repos)))
            
            for repo in enrolled_repos:
                try:
                    await self._analyze_repository_changes(repo.id)
                except Exception as e:
                    _log.error(s_("Failed to analyze repository", repo_id=repo.id, error=str(e)), exc_info=e)
                    
        except Exception as e:
            _log.error(s_("Failed to run daily analysis"), exc_info=e)

    async def _analyze_repository_changes(self, repo_id: str):
        _log.info(s_("Starting change analysis for repository", repo_id=repo_id))
        
        # Check if analysis already exists for today
        existing_analysis = await self._get_todays_analysis(repo_id)
        if existing_analysis is not None:
            _log.info(s_("Analysis already exists for today", repo_id=repo_id, analysis_id=existing_analysis.id))
            return

        # Create new analysis record
        analysis = RepoChangeAnalysis()
        analysis.id = str(uuid.uuid4())
        analysis.repo_id = repo_id
        analysis.status = "pending"
        analysis.created_at.FromDatetime(self._clock.now())
        analysis.updated_at.FromDatetime(self._clock.now())

        try:
            # Store the analysis record
            analysis = await self._storage.create_repo_change_analysis(analysis)
            _log.info(s_("Created analysis record", analysis_id=analysis.id, repo_id=repo_id))

            # Get repository information
            repo = await self._storage.get_github_repo(repo_id)
            if repo is None:
                raise ValueError(f"Repository with id {repo_id} not found")

            # Track analysis started
            await self._analytics.track_analysis_started(repo_id, repo.full_name, analysis.id)

            # Get recent changes from GitHub
            changes = await self._get_recent_changes(repo_id)
            
            # Generate AI summary
            summary = await self._generate_change_summary(repo, changes)
            
            # Store summary as observation
            observation_key = await self._store_summary_as_observation(repo, summary)
            
            # Update analysis record with success
            await self._storage.set_repo_change_analysis_observation(analysis.id, observation_key)
            await self._storage.update_repo_change_analysis_status(analysis.id, "completed")
            
            # Track successful completion
            await self._analytics.track_analysis_completed(
                repo_id, 
                repo.full_name, 
                analysis.id,
                len(changes.get('commits', [])),
                len(changes.get('merged_prs', [])),
                len(summary)
            )
            
            _log.info(s_("Successfully completed change analysis", analysis_id=analysis.id, repo_id=repo_id))
            
        except Exception as e:
            # Update analysis record with error
            await self._storage.update_repo_change_analysis_status(analysis.id, "failed", str(e))
            
            # Track failure
            repo = await self._storage.get_github_repo(repo_id)
            error_type = type(e).__name__
            if repo:
                await self._analytics.track_analysis_failed(
                    repo_id, 
                    repo.full_name, 
                    analysis.id, 
                    str(e), 
                    error_type
                )
            
            _log.error(s_("Failed to complete change analysis", 
                         analysis_id=analysis.id, 
                         repo_id=repo_id, 
                         error=str(e),
                         error_type=error_type), exc_info=e)
            raise

    async def _get_todays_analysis(self, repo_id: str) -> Optional[RepoChangeAnalysis]:
        analyses = await self._storage.get_repo_change_analyses_by_repo(repo_id)
        today = self._clock.now().date()
        
        for analysis in analyses:
            if analysis.HasField("analyzed_at"):
                analysis_date = analysis.analyzed_at.ToDatetime().date()
                if analysis_date == today:
                    return analysis
        return None

    async def _get_recent_changes(self, repo_id: str) -> List[dict]:
        # Get the last analysis date to determine the time range
        analyses = await self._storage.get_repo_change_analyses_by_repo(repo_id)
        
        # Default to last 24 hours if no previous analysis
        since_date = self._clock.now() - timedelta(days=1)
        
        if analyses:
            # Get the most recent successful analysis
            for analysis in analyses:
                if analysis.status == "completed" and analysis.HasField("analyzed_at"):
                    since_date = analysis.analyzed_at.ToDatetime()
                    break
        
        repo = await self._storage.get_github_repo(repo_id)
        if repo is None:
            raise ValueError(f"Repository with id {repo_id} not found")
        
        # Get commits and merged PRs since the last analysis
        commits = await self._github_provider.get_commits_since(repo.full_name, since_date)
        merged_prs = await self._github_provider.get_merged_prs_since(repo.full_name, since_date)
        
        return {
            "commits": commits,
            "merged_prs": merged_prs,
            "since_date": since_date.isoformat(),
            "repo_name": repo.full_name
        }

    async def _generate_change_summary(self, repo, changes: dict) -> str:
        from dev_observer.prompts.provider import FormattedPrompt, PromptComponent
        from dev_observer.api.types.ai_pb2 import ModelConfig
        
        # Create a prompt for AI summarization
        prompt_text = f"""Generate a natural language summary of recent changes to the repository {changes['repo_name']}.

Changes since {changes['since_date']}:

Commits ({len(changes['commits'])}):
{self._format_commits(changes['commits'])}

Merged Pull Requests ({len(changes['merged_prs'])}):
{self._format_prs(changes['merged_prs'])}

Please provide a concise summary focusing on:
1. What was changed or added
2. Any significant features or fixes
3. Overall impact or theme of the changes

If there are no significant changes, please indicate that."""
        
        # Get global config to determine model settings
        global_config = await self._storage.get_global_config()
        model_config = None
        
        if global_config.HasField("analysis") and global_config.analysis.HasField("model"):
            model_config = global_config.analysis.model
        else:
            # Default model configuration
            model_config = ModelConfig()
            model_config.provider = "openai"
            model_config.model_name = "gpt-4"
        
        # Create formatted prompt
        formatted_prompt = FormattedPrompt(
            user=PromptComponent(text=prompt_text),
            config=type('PromptConfig', (), {})()
        )
        formatted_prompt.config.model = model_config
        
        try:
            # Use the analysis provider to generate the summary
            result = await self._analysis_provider.analyze(formatted_prompt)
            summary = result.analysis
            
            if not summary or summary.strip() == "":
                return f"No significant changes detected in {repo.full_name} since {changes['since_date']}"
            
            return summary
            
        except Exception as e:
            _log.error(s_("Failed to generate AI summary", repo=repo.full_name, error=str(e)), exc_info=e)
            # Return fallback summary
            return self._generate_fallback_summary(repo, changes)

    def _format_commits(self, commits: List[dict]) -> str:
        if not commits:
            return "No commits found"
        
        formatted = []
        for commit in commits[:10]:  # Limit to 10 most recent
            formatted.append(f"- {commit.get('message', 'No message')} ({commit.get('author', 'Unknown')})")
        
        if len(commits) > 10:
            formatted.append(f"... and {len(commits) - 10} more commits")
        
        return "\n".join(formatted)

    def _format_prs(self, prs: List[dict]) -> str:
        if not prs:
            return "No merged pull requests found"
        
        formatted = []
        for pr in prs:
            formatted.append(f"- #{pr.get('number', 'N/A')}: {pr.get('title', 'No title')} ({pr.get('user', 'Unknown')})")
        
        return "\n".join(formatted)

    async def _store_summary_as_observation(self, repo, summary: str) -> str:
        # Generate unique observation key
        date_str = self._clock.now().strftime("%Y-%m-%d")
        observation_key = f"{repo.full_name}/change-summary/{date_str}"
        
        # Store as observation
        key = ObservationKey(
            kind="repo_change_summaries",
            name="daily_summary",
            key=observation_key
        )
        
        await self._observations_provider.store_observation(key, summary)
        return observation_key

    def _generate_fallback_summary(self, repo, changes: dict) -> str:
        """Generate a basic summary without AI when AI analysis fails"""
        commits_count = len(changes['commits'])
        prs_count = len(changes['merged_prs'])
        
        if commits_count == 0 and prs_count == 0:
            return f"No significant changes detected in {repo.full_name} since {changes['since_date']}"
        
        summary_parts = []
        
        if commits_count > 0:
            summary_parts.append(f"{commits_count} commits")
        
        if prs_count > 0:
            summary_parts.append(f"{prs_count} merged pull requests")
        
        summary = f"Repository {repo.full_name} had {' and '.join(summary_parts)} since {changes['since_date']}."
        
        # Add some commit details if available
        if changes['commits']:
            recent_commit = changes['commits'][0]
            summary += f" Latest commit: \"{recent_commit.get('message', 'No message')}\" by {recent_commit.get('author', 'Unknown')}."
        
        # Add PR details if available
        if changes['merged_prs']:
            recent_pr = changes['merged_prs'][0]
            summary += f" Latest merged PR: #{recent_pr.get('number', 'N/A')} \"{recent_pr.get('title', 'No title')}\"."
        
        return summary