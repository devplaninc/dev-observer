import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from github import Github
from google.protobuf.timestamp_pb2 import Timestamp
from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.types.ai_pb2 import PromptConfig, SystemMessage, UserMessage, ModelConfig
from dev_observer.api.types.observations_pb2 import Observation, ObservationKey
from dev_observer.api.types.repo_pb2 import GitHubRepository, ChangeAnalysisConfig, GitProperties
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.prompts.provider import FormattedPrompt, PromptsProvider
from dev_observer.repository.provider import GitRepositoryProvider
from dev_observer.repository.types import ObservedRepo
from dev_observer.storage.provider import StorageProvider
from dev_observer.storage.postgresql.model import RepoChangeAnalysisEntity
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class ChangeAnalysisProcessor:
    """Processor for handling daily change analysis of enrolled repositories."""

    _storage: StorageProvider
    _observations: ObservationsProvider
    _github_provider: Optional[GitRepositoryProvider]
    _analysis_provider: Optional[AnalysisProvider]
    _prompts_provider: Optional[PromptsProvider]
    _clock: Clock

    def __init__(self, 
                 storage: StorageProvider, 
                 observations: ObservationsProvider,
                 github_provider: Optional[GitRepositoryProvider] = None,
                 analysis_provider: Optional[AnalysisProvider] = None,
                 prompts_provider: Optional[PromptsProvider] = None,
                 clock: Clock = RealClock()):
        self._storage = storage
        self._observations = observations
        self._github_provider = github_provider
        self._analysis_provider = analysis_provider
        self._prompts_provider = prompts_provider
        self._clock = clock

    async def schedule_daily_analysis(self):
        """Schedule daily analysis for all enrolled repositories."""
        try:
            enrolled_repos = await self._storage.get_enrolled_repositories()
            _log.info(s_("Scheduling daily analysis", repo_count=len(enrolled_repos)))

            for repo in enrolled_repos:
                await self._schedule_repo_analysis(repo)

        except Exception as e:
            _log.error(s_("Failed to schedule daily analysis", error=str(e)), exc_info=e)

    async def _schedule_repo_analysis(self, repo: GitHubRepository):
        """Schedule analysis for a specific repository if not already done today."""
        try:
            # Check if analysis already exists for today
            today = self._clock.now().date()
            existing_records = await self._storage.get_change_analysis_records(
                repo_id=repo.id,
                status=None  # Get all statuses
            )

            # Check if there's already a record for today
            for record in existing_records:
                if record.created_at.date() == today:
                    _log.debug(s_("Analysis already scheduled for today", repo_id=repo.id))
                    return

            # Create new analysis record
            analysis_record = RepoChangeAnalysisEntity(
                id=str(uuid.uuid4()),
                repo_id=repo.id,
                status="pending",
                observation_key=None,
                error_message=None,
                analyzed_at=None
            )

            await self._storage.create_change_analysis_record(analysis_record)
            _log.info(s_("Scheduled change analysis", repo_id=repo.id, analysis_id=analysis_record.id))

        except Exception as e:
            _log.error(s_("Failed to schedule repo analysis", repo_id=repo.id, error=str(e)), exc_info=e)

    async def process_pending_analysis(self):
        """Process all pending change analysis records."""
        try:
            pending_records = await self._storage.get_change_analysis_records(status="pending")
            _log.info(s_("Processing pending analysis", count=len(pending_records)))

            for record in pending_records:
                await self._process_analysis_record(record)

        except Exception as e:
            _log.error(s_("Failed to process pending analysis", error=str(e)), exc_info=e)

    async def _process_analysis_record(self, record: RepoChangeAnalysisEntity):
        """Process a single analysis record."""
        try:
            _log.info(s_("Processing analysis record", analysis_id=record.id, repo_id=record.repo_id))

            # Get repository
            repo = await self._storage.get_github_repo(record.repo_id)
            if not repo:
                error_msg = f"Repository {record.repo_id} not found"
                await self._mark_analysis_failed(record, error_msg)
                return

            # Check if repository is still enrolled
            if not (repo.properties and 
                    repo.properties.change_analysis and 
                    repo.properties.change_analysis.enrolled):
                error_msg = "Repository is no longer enrolled for change analysis"
                await self._mark_analysis_failed(record, error_msg)
                return

            # Generate AI summary
            summary = await self._generate_change_summary(repo)

            # Store summary as observation
            observation_key = f"change_summary_{repo.full_name}_{record.id}"
            observation = Observation(
                key=ObservationKey(
                    kind="change_analysis",
                    name="daily_summary",
                    key=observation_key
                ),
                content=summary
            )

            await self._observations.store(observation)

            # Update analysis record
            record.status = "completed"
            record.observation_key = observation_key
            record.analyzed_at = self._clock.now()

            await self._storage.update_change_analysis_record(record)

            # Update repository's last analysis time
            await self._update_repo_last_analysis(repo)

            _log.info(s_("Analysis completed successfully", analysis_id=record.id, repo_id=record.repo_id))

        except Exception as e:
            error_msg = f"Failed to process analysis: {str(e)}"
            _log.error(s_("Analysis processing failed", analysis_id=record.id, error=error_msg), exc_info=e)
            await self._mark_analysis_failed(record, error_msg)

    async def _generate_change_summary(self, repo: GitHubRepository) -> str:
        """Generate AI-powered change summary for the repository."""
        try:
            # Determine the analysis period
            last_analysis = None
            if (repo.properties and 
                repo.properties.change_analysis and 
                repo.properties.change_analysis.last_analysis):
                last_analysis = repo.properties.change_analysis.last_analysis.ToDatetime()

            # If no previous analysis, analyze last 24 hours
            if not last_analysis:
                last_analysis = self._clock.now() - timedelta(days=1)

            current_time = self._clock.now()

            # Fetch GitHub data if providers are available
            commits_data = ""
            prs_data = ""

            if self._github_provider:
                try:
                    commits_data, prs_data = await self._fetch_github_changes(repo, last_analysis, current_time)
                except Exception as e:
                    _log.warning(s_("Failed to fetch GitHub data", repo_id=repo.id, error=str(e)))
                    commits_data = f"Error fetching commits: {str(e)}"
                    prs_data = f"Error fetching pull requests: {str(e)}"

            # Use AI analysis if available, otherwise fall back to structured summary
            if self._analysis_provider and self._prompts_provider:
                try:
                    return await self._generate_ai_summary(repo, last_analysis, current_time, commits_data, prs_data)
                except Exception as e:
                    _log.warning(s_("Failed to generate AI summary, falling back to structured summary", repo_id=repo.id, error=str(e)))

            # Fallback to structured summary
            return self._generate_structured_summary(repo, last_analysis, current_time, commits_data, prs_data)

        except Exception as e:
            _log.error(s_("Failed to generate change summary", repo_id=repo.id, error=str(e)), exc_info=e)
            # Return a basic summary on error
            return f"Change analysis for {repo.full_name} completed on {self._clock.now().strftime('%Y-%m-%d %H:%M:%S')}. Error occurred during detailed analysis: {str(e)}"

    async def _fetch_github_changes(self, repo: GitHubRepository, since: datetime, until: datetime) -> tuple[str, str]:
        """Fetch commits and pull requests from GitHub API."""
        try:
            # Create ObservedRepo for GitHub provider
            observed_repo = ObservedRepo(url=repo.url, github_repo=repo)

            # Get repository info and authentication
            repo_info = await self._github_provider.get_repo(observed_repo)

            # Use GitHub API directly to fetch commits and PRs
            # We need to get the auth from the GitHub provider
            if hasattr(self._github_provider, '_auth_provider'):
                auth = await self._github_provider._auth_provider.get_auth(observed_repo)

                with Github(auth=auth) as gh:
                    gh_repo = gh.get_repo(repo.full_name)

                    # Fetch commits since last analysis
                    commits = list(gh_repo.get_commits(since=since, until=until))
                    commits_data = self._format_commits_data(commits)

                    # Fetch merged pull requests since last analysis
                    prs = list(gh_repo.get_pulls(state='closed', sort='updated', direction='desc'))
                    # Filter for merged PRs in the time range
                    merged_prs = [
                        pr for pr in prs 
                        if pr.merged_at and since <= pr.merged_at <= until
                    ]
                    prs_data = self._format_prs_data(merged_prs)

                    return commits_data, prs_data
            else:
                return "GitHub authentication not available", "GitHub authentication not available"

        except Exception as e:
            _log.error(s_("Failed to fetch GitHub changes", repo_id=repo.id, error=str(e)), exc_info=e)
            return f"Error fetching commits: {str(e)}", f"Error fetching pull requests: {str(e)}"

    def _format_commits_data(self, commits) -> str:
        """Format commits data for analysis."""
        if not commits:
            return "No commits found in the analysis period."

        formatted_commits = []
        for commit in commits[:20]:  # Limit to 20 most recent commits
            commit_info = f"- **{commit.sha[:8]}** by {commit.author.login if commit.author else 'Unknown'}: {commit.commit.message.split(chr(10))[0]}"
            if commit.commit.committer:
                commit_info += f" (committed on {commit.commit.committer.date.strftime('%Y-%m-%d %H:%M')})"
            formatted_commits.append(commit_info)

        result = f"Found {len(commits)} commits:\n" + "\n".join(formatted_commits)
        if len(commits) > 20:
            result += f"\n... and {len(commits) - 20} more commits"

        return result

    def _format_prs_data(self, prs) -> str:
        """Format pull requests data for analysis."""
        if not prs:
            return "No merged pull requests found in the analysis period."

        formatted_prs = []
        for pr in prs[:10]:  # Limit to 10 most recent PRs
            pr_info = f"- **#{pr.number}** {pr.title} by {pr.user.login}"
            pr_info += f" (merged on {pr.merged_at.strftime('%Y-%m-%d %H:%M')})"
            if pr.body and len(pr.body.strip()) > 0:
                # Include first line of PR description
                first_line = pr.body.split('\n')[0].strip()
                if len(first_line) > 100:
                    first_line = first_line[:100] + "..."
                pr_info += f"\n  Description: {first_line}"
            formatted_prs.append(pr_info)

        result = f"Found {len(prs)} merged pull requests:\n" + "\n".join(formatted_prs)
        if len(prs) > 10:
            result += f"\n... and {len(prs) - 10} more pull requests"

        return result

    async def _generate_ai_summary(self, repo: GitHubRepository, last_analysis: datetime, current_time: datetime, commits_data: str, prs_data: str) -> str:
        """Generate AI-powered summary using Langgraph/Langchain."""
        try:
            # Create the prompt for AI analysis
            system_prompt = """You are an expert software development analyst. Your task is to analyze GitHub repository changes and provide a comprehensive, natural language summary.

Focus on:
1. Key changes and their impact
2. Development patterns and trends
3. Notable commits and pull requests
4. Overall project evolution
5. Potential risks or improvements

Provide a clear, professional summary that would be valuable for project stakeholders."""

            user_prompt = f"""Please analyze the following changes for the repository {repo.full_name}:

**Repository Information:**
- Repository: {repo.full_name}
- URL: {repo.url}
- Description: {repo.description or 'No description available'}

**Analysis Period:** {last_analysis.strftime('%Y-%m-%d %H:%M')} to {current_time.strftime('%Y-%m-%d %H:%M')}

**Commits:**
{commits_data}

**Merged Pull Requests:**
{prs_data}

Please provide a comprehensive analysis of these changes, highlighting the most important developments, patterns, and insights."""

            # Create FormattedPrompt
            prompt_config = PromptConfig(
                model=ModelConfig(
                    provider="openai",
                    model_name="gpt-4"
                )
            )

            formatted_prompt = FormattedPrompt(
                config=prompt_config,
                system=SystemMessage(text=system_prompt),
                user=UserMessage(text=user_prompt)
            )

            # Use analysis provider to generate summary
            result = await self._analysis_provider.analyze(formatted_prompt)
            return result.analysis

        except Exception as e:
            _log.error(s_("Failed to generate AI summary", repo_id=repo.id, error=str(e)), exc_info=e)
            raise

    def _generate_structured_summary(self, repo: GitHubRepository, last_analysis: datetime, current_time: datetime, commits_data: str, prs_data: str) -> str:
        """Generate structured summary as fallback."""
        summary_parts = []
        summary_parts.append(f"# Change Analysis Report for {repo.full_name}")
        summary_parts.append(f"**Analysis Period:** {last_analysis.strftime('%Y-%m-%d %H:%M')} to {current_time.strftime('%Y-%m-%d %H:%M')}")
        summary_parts.append("")

        # Repository information
        summary_parts.append("## Repository Information")
        summary_parts.append(f"- **Repository:** {repo.full_name}")
        summary_parts.append(f"- **URL:** {repo.url}")
        if repo.description:
            summary_parts.append(f"- **Description:** {repo.description}")
        summary_parts.append("")

        # Analysis summary
        summary_parts.append("## Change Summary")
        summary_parts.append("")

        summary_parts.append("### Commits")
        summary_parts.append(commits_data)
        summary_parts.append("")

        summary_parts.append("### Pull Requests")
        summary_parts.append(prs_data)
        summary_parts.append("")

        summary_parts.append("### Status")
        summary_parts.append(f"- **Analysis completed:** {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        summary_parts.append(f"- **Next analysis:** Scheduled for next day at 09:00")

        return "\n".join(summary_parts)

    async def _mark_analysis_failed(self, record: RepoChangeAnalysisEntity, error_message: str):
        """Mark an analysis record as failed."""
        record.status = "failed"
        record.error_message = error_message
        record.analyzed_at = self._clock.now()
        await self._storage.update_change_analysis_record(record)

    async def _update_repo_last_analysis(self, repo: GitHubRepository):
        """Update the repository's last analysis timestamp."""
        properties = repo.properties if repo.properties else GitProperties()
        if not properties.change_analysis:
            properties.change_analysis = ChangeAnalysisConfig()

        # Convert datetime to protobuf timestamp
        timestamp = Timestamp()
        timestamp.FromDatetime(self._clock.now())
        properties.change_analysis.last_analysis.CopyFrom(timestamp)

        await self._storage.update_repo_properties(repo.id, properties)
