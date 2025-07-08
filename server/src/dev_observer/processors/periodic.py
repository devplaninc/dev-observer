import asyncio
import logging
from datetime import timedelta, datetime, time
from typing import List, Optional

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.types.processing_pb2 import ProcessingItem
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.change_analysis import ChangeAnalysisProcessor
from dev_observer.processors.flattening import ObservationRequest
from dev_observer.processors.repos import ReposProcessor
from dev_observer.repository.types import ObservedRepo
from dev_observer.processors.websites import WebsitesProcessor, ObservedWebsite
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock
from dev_observer.website.cloner import normalize_domain, normalize_name

_log = logging.getLogger(__name__)

class PeriodicProcessor:
    _storage: StorageProvider
    _repos_processor: ReposProcessor
    _websites_processor: Optional[WebsitesProcessor]
    _change_analysis_processor: Optional[ChangeAnalysisProcessor]
    _clock: Clock
    _last_daily_schedule: Optional[datetime]

    def __init__(self,
                 storage: StorageProvider,
                 repos_processor: ReposProcessor,
                 observations: Optional[ObservationsProvider] = None,
                 websites_processor: Optional[WebsitesProcessor] = None,
                 github_provider = None,
                 analysis_provider = None,
                 prompts_provider = None,
                 clock: Clock = RealClock(),
                 ):
        self._storage = storage
        self._repos_processor = repos_processor
        self._websites_processor = websites_processor
        self._clock = clock
        self._last_daily_schedule = None

        # Initialize change analysis processor if observations provider is available
        if observations:
            self._change_analysis_processor = ChangeAnalysisProcessor(
                storage, 
                observations, 
                github_provider=github_provider,
                analysis_provider=analysis_provider,
                prompts_provider=prompts_provider,
                clock=clock
            )
        else:
            self._change_analysis_processor = None

    async def run(self):
        # TODO: add proper background processing
        _log.info("Starting periodic processor")
        while True:
            try:
                # Check if we need to schedule daily change analysis
                await self._check_daily_schedule()

                # Process pending change analysis
                if self._change_analysis_processor:
                    await self._change_analysis_processor.process_pending_analysis()

                # Process regular items
                await self.process_next()
            except Exception as e:
                _log.error(s_("Failed to process next item"), exc_info=e)
            await asyncio.sleep(5)

    async def _check_daily_schedule(self):
        """Check if we need to schedule daily change analysis."""
        if not self._change_analysis_processor:
            return

        now = self._clock.now()

        # Check if we should schedule daily analysis (once per day at a specific time)
        # Let's schedule at 9:00 AM daily
        target_time = time(9, 0)  # 9:00 AM

        # If we haven't scheduled today or it's past the target time and we haven't scheduled yet
        if (self._last_daily_schedule is None or 
            self._last_daily_schedule.date() < now.date() or
            (now.time() >= target_time and 
             (self._last_daily_schedule is None or self._last_daily_schedule.date() < now.date()))):

            try:
                await self._change_analysis_processor.schedule_daily_analysis()
                self._last_daily_schedule = now
                _log.info(s_("Daily change analysis scheduled", timestamp=now))
            except Exception as e:
                _log.error(s_("Failed to schedule daily change analysis", error=str(e)), exc_info=e)

    async def process_next(self) -> Optional[ProcessingItem]:
        item = await self._storage.next_processing_item()
        if item is None:
            return None
        _log.info(s_("Processing item", item=item))
        retry_time = self._clock.now() + timedelta(minutes=30)
        # prevent from running again right away.
        await self._storage.set_next_processing_time(item.key, retry_time)
        await self._process_item(item)
        return item

    async def _process_item(self, item: ProcessingItem):
        ent_type = item.key.WhichOneof("entity")
        if ent_type == "github_repo_id":
            await self._process_github_repo(item.key.github_repo_id)
        elif ent_type == "website_url":
            if self._websites_processor is None:
                _log.error(s_("Website processor is not configured", url=item.key.website_url))
                raise ValueError(f"Website processor is not configured")
            await self._process_website(item.key.website_url)
        else:
            raise ValueError(f"[{ent_type}] is not supported")
        await self._storage.set_next_processing_time(item.key, None)

    async def _process_github_repo(self, repo_id: str):
        config = await self._storage.get_global_config()
        if config.HasField("repo_analysis") and config.repo_analysis.disabled:
            _log.warning(s_("Repo analysis disabled"))
            return

        repo = await self._storage.get_github_repo(repo_id)
        if repo is None:
            _log.error(s_("Github repo not found", repo_id=repo_id))
            raise ValueError(f"Repo with id [{repo_id}] is not found")
        _log.debug(s_("Processing github repo", repo=repo))
        requests: List[ObservationRequest] = []
        for analyzer in config.analysis.repo_analyzers:
            key = f"{repo.full_name}/{analyzer.file_name}"
            requests.append(ObservationRequest(
                prompt_prefix=analyzer.prompt_prefix,
                key=ObservationKey(kind="repos", name=analyzer.file_name, key=key),
            ))
        if len(requests) == 0:
            _log.debug(s_("No analyzers configured, skipping", repo=repo))
            return
        await self._repos_processor.process(ObservedRepo(url=repo.url, github_repo=repo), requests, config)
        _log.debug(s_("Github repo processed", repo=repo))

    async def _process_website(self, website_url: str):
        _log.debug(s_("Processing website", url=website_url))
        requests: List[ObservationRequest] = []
        config = await self._storage.get_global_config()

        for analyzer in config.analysis.site_analyzers:
            domain = normalize_domain(website_url)
            name = normalize_name(website_url)
            key = f"{domain}/{name}/{analyzer.file_name}"

            requests.append(ObservationRequest(
                prompt_prefix=analyzer.prompt_prefix,
                key=ObservationKey(kind="websites", name=analyzer.file_name, key=key),
            ))

        if len(requests) == 0:
            _log.debug(s_("No analyzers configured, skipping", url=website_url))
            return

        await self._websites_processor.process(ObservedWebsite(url=website_url), requests, config)
        _log.debug(s_("Website processed", url=website_url))
