import asyncio
import datetime
import logging
import uuid
from datetime import timedelta
from typing import List, Optional

from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.api.types.repo_pb2 import GitHubRepository
from dev_observer.log import s_
from dev_observer.storage.postgresql.model import RepoChangeAnalysisEntity, RepoChangeAnalysisStatus
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock
from dev_observer.repository.github import GithubProvider
from dev_observer.repository.types import ObservedRepo
from dev_observer.repository.parser import parse_github_url
from github import Github
from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.observations.provider import ObservationsProvider

_log = logging.getLogger(__name__)


class ChangeAnalysisScheduler:
    """Scheduler for daily change analysis of enrolled repositories."""
    
    _storage: StorageProvider
    _clock: Clock
    _analysis_interval: timedelta
    _analysis: AnalysisProvider
    _prompts: PromptsProvider
    _observations: ObservationsProvider
    
    def __init__(self, 
                 storage: StorageProvider, 
                 analysis: AnalysisProvider,
                 prompts: PromptsProvider,
                 observations: ObservationsProvider,
                 clock: Clock = RealClock(),
                 analysis_interval: timedelta = timedelta(days=1)):
        self._storage = storage
        self._analysis = analysis
        self._prompts = prompts
        self._observations = observations
        self._clock = clock
        self._analysis_interval = analysis_interval
    
    async def run(self):
        """Run the scheduler in a loop, processing enrolled repositories daily."""
        _log.info("Starting change analysis scheduler")
        while True:
            try:
                await self._process_daily_analysis()
            except Exception as e:
                _log.error(s_("Failed to process daily analysis"), exc_info=e)
            
            # Sleep until next analysis cycle
            next_run = self._clock.now() + self._analysis_interval
            _log.info(s_("Next analysis run scheduled", next_run=next_run))
            await asyncio.sleep(self._analysis_interval.total_seconds())
    
    async def _process_daily_analysis(self):
        """Process daily analysis for all enrolled repositories."""
        _log.info("Starting daily change analysis")
        
        # Get all enrolled repositories
        enrolled_repos = await self._get_enrolled_repositories()
        _log.info(s_("Found enrolled repositories", count=len(enrolled_repos)))
        
        # Create or update analysis jobs for each enrolled repo
        for repo in enrolled_repos:
            try:
                await self._ensure_analysis_job(repo)
            except Exception as e:
                _log.error(s_("Failed to create analysis job", repo_id=repo.id), exc_info=e)
        
        # Process pending jobs (in a real implementation, this might be done by a separate worker)
        await self._process_pending_jobs()
    
    async def _get_enrolled_repositories(self) -> List[GitHubRepository]:
        """Get all repositories that are enrolled for change analysis."""
        all_repos = await self._storage.get_github_repos()
        enrolled = []
        
        for repo in all_repos:
            if hasattr(repo, 'change_analysis_enrolled') and repo.change_analysis_enrolled:
                enrolled.append(repo)
        
        return enrolled
    
    async def _ensure_analysis_job(self, repo: GitHubRepository):
        """Ensure an analysis job exists for today for the given repository."""
        today = self._clock.now().date()
        
        # Check if job already exists for today
        existing_job = await self._get_today_analysis_job(repo.id, today)
        if existing_job:
            _log.debug(s_("Analysis job already exists for today", repo_id=repo.id, job_id=existing_job.id))
            return
        
        # Create new analysis job
        job = RepoChangeAnalysisEntity(
            id=str(uuid.uuid4()),
            repo_id=repo.id,
            status=RepoChangeAnalysisStatus.pending,
            analyzed_at=None,
            error_message=None,
            observation_key=None
        )
        
        await self._create_analysis_job(job)
        _log.info(s_("Created analysis job", repo_id=repo.id, job_id=job.id))
    
    async def _get_today_analysis_job(self, repo_id: str, date: datetime.date) -> Optional[RepoChangeAnalysisEntity]:
        """Get the analysis job for a repository on a specific date."""
        return await self._storage.get_today_analysis_job(repo_id, date)
    
    async def _create_analysis_job(self, job: RepoChangeAnalysisEntity):
        """Create a new analysis job in the database."""
        await self._storage.create_change_analysis_job(job)
    
    async def _process_pending_jobs(self):
        """Process all pending analysis jobs."""
        pending_jobs = await self._storage.get_change_analysis_jobs(status="pending")
        _log.info(s_("Processing pending jobs", count=len(pending_jobs)))
        
        processor = ChangeAnalysisProcessor(self._storage, self._analysis, self._prompts, self._observations, self._clock)
        for job in pending_jobs:
            try:
                await processor.process_job(job)
            except Exception as e:
                _log.error(s_("Failed to process job", job_id=job.id), exc_info=e)


class ChangeAnalysisProcessor:
    """Processor for individual change analysis jobs."""
    
    _storage: StorageProvider
    _analysis: AnalysisProvider
    _prompts: PromptsProvider
    _observations: ObservationsProvider
    _clock: Clock
    
    def __init__(self, storage: StorageProvider, analysis: AnalysisProvider, prompts: PromptsProvider, observations: ObservationsProvider, clock: Clock = RealClock()):
        self._storage = storage
        self._analysis = analysis
        self._prompts = prompts
        self._observations = observations
        self._clock = clock
    
    async def process_job(self, job: RepoChangeAnalysisEntity) -> bool:
        """Process a single analysis job."""
        try:
            _log.info(s_("Processing analysis job", job_id=job.id, repo_id=job.repo_id))
            
            # Get the repository
            repo = await self._storage.get_github_repo(job.repo_id)
            if not repo:
                await self._mark_job_failed(job, f"Repository {job.repo_id} not found")
                return False
            
            # Find last completed analysis for this repo
            last_completed = await self._get_last_completed_analysis(repo.id)
            since = last_completed.analyzed_at if last_completed else None
            
            # Fetch merged PRs and commits since last analysis
            try:
                pr_list, commit_list = await self._fetch_github_changes(repo, since)
            except Exception as e:
                await self._mark_job_failed(job, f"Failed to fetch PRs/commits: {e}")
                return False
            
            # Generate summary using Langgraph/Langchain
            try:
                summary = await self._generate_summary(repo, pr_list, commit_list, since)
            except Exception as e:
                await self._mark_job_failed(job, f"AI summarization failed: {e}")
                return False
            
            # Store summary as observation
            observation_key = await self._store_summary_observation(repo, summary)
            
            # Update job with success
            await self._mark_job_completed(job, observation_key)
            
            # Analytics logging
            _log.info(s_("Change analysis completed", 
                        job_id=job.id, 
                        repo_id=repo.id, 
                        repo_name=repo.full_name,
                        pr_count=len(pr_list),
                        commit_count=len(commit_list),
                        observation_key=observation_key))
            
            return True
            
        except Exception as e:
            _log.error(s_("Analysis job failed", job_id=job.id), exc_info=e)
            await self._mark_job_failed(job, str(e))
            
            # Analytics logging for failure
            _log.error(s_("Change analysis failed", 
                         job_id=job.id, 
                         repo_id=job.repo_id,
                         error=str(e)))
            
            return False

    async def _get_last_completed_analysis(self, repo_id: str) -> Optional[RepoChangeAnalysisEntity]:
        jobs = await self._storage.get_change_analysis_jobs(repo_id=repo_id, status="completed")
        if not jobs:
            return None
        # Return the most recent completed job
        return max(jobs, key=lambda j: j.analyzed_at or datetime.datetime.min)

    async def _fetch_github_changes(self, repo: GitHubRepository, since: Optional[datetime.datetime]):
        """Fetch merged PRs and commits since the given date."""
        # Use PyGithub directly for now
        parsed = parse_github_url(repo.url)
        # TODO: Use the correct auth (token/app) from settings
        # For now, use a personal token from env
        import os
        token = os.environ.get("DEV_OBSERVER__GIT__GITHUB__PERSONAL_TOKEN")
        if not token:
            raise RuntimeError("GitHub token not configured")
        gh = Github(token)
        gh_repo = gh.get_repo(f"{parsed.owner}/{parsed.name}")
        pr_list = []
        commit_list = []
        # Fetch merged PRs
        for pr in gh_repo.get_pulls(state="closed", sort="updated", direction="desc"):
            if pr.merged_at and (since is None or pr.merged_at.replace(tzinfo=None) > since):
                pr_list.append({
                    "number": pr.number,
                    "title": pr.title,
                    "user": pr.user.login if pr.user else None,
                    "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                    "body": pr.body,
                    "url": pr.html_url,
                })
            elif since and pr.updated_at.replace(tzinfo=None) <= since:
                break  # PRs are sorted by updated_at desc
        # Fetch commits
        for commit in gh_repo.get_commits(since=since) if since else gh_repo.get_commits():
            commit_list.append({
                "sha": commit.sha,
                "author": commit.author.login if commit.author else None,
                "date": commit.commit.author.date.isoformat(),
                "message": commit.commit.message,
                "url": commit.html_url,
            })
        return pr_list, commit_list

    async def _generate_summary(self, repo: GitHubRepository, pr_list, commit_list, since) -> str:
        """Generate a summary of changes for the repository using AI."""
        if not pr_list and not commit_list:
            return "No significant changes since last analysis."
        
        # Format the data for the prompt
        current_date = self._clock.now().strftime('%Y-%m-%d')
        last_analysis_date = since.strftime('%Y-%m-%d') if since else "beginning"
        
        # Format PRs and commits for the prompt
        merged_prs = ""
        if pr_list:
            merged_prs = "\n".join([
                f"- #{pr['number']}: {pr['title']} (by {pr['user']}) at {pr['merged_at']}"
                for pr in pr_list
            ])
        
        commits = ""
        if commit_list:
            commits = "\n".join([
                f"- {c['sha'][:7]}: {c['message'].splitlines()[0]} (by {c['author']}) at {c['date']}"
                for c in commit_list
            ])
        
        # Format prompt using the prompts provider
        prompt = await self._prompts.get_formatted(
            "change_analysis_summary",
            {
                "repo_name": repo.full_name,
                "last_analysis_date": last_analysis_date,
                "current_date": current_date,
                "merged_prs": merged_prs,
                "commits": commits,
            }
        )
        result = await self._analysis.analyze(prompt)
        return result.analysis
    
    async def _store_summary_observation(self, repo: GitHubRepository, summary: str) -> str:
        """Store the summary as an observation and return the observation key."""
        # Create observation key
        observation_key = f"change_summary/{repo.full_name}/{self._clock.now().strftime('%Y-%m-%d')}"
        
        # Create observation
        observation = Observation(
            key=ObservationKey(
                kind="change_summary",
                name=repo.full_name,
                key=observation_key
            ),
            content=summary
        )
        
        # Store observation using observations provider
        await self._observations.store(observation)
        _log.info(s_("Stored change summary observation", key=observation_key, repo=repo.full_name))
        
        return observation_key
    
    async def _mark_job_completed(self, job: RepoChangeAnalysisEntity, observation_key: str):
        """Mark a job as completed."""
        job.status = RepoChangeAnalysisStatus.completed
        job.observation_key = observation_key
        job.analyzed_at = self._clock.now()
        job.error_message = None
        
        await self._storage.update_change_analysis_job(job)
    
    async def _mark_job_failed(self, job: RepoChangeAnalysisEntity, error_message: str):
        """Mark a job as failed."""
        job.status = RepoChangeAnalysisStatus.failed
        job.error_message = error_message
        job.analyzed_at = self._clock.now()
        
        await self._storage.update_change_analysis_job(job) 