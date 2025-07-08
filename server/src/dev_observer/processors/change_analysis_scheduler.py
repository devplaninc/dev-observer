import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Optional

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.change_analysis import ChangeAnalysisProcessor
from dev_observer.repository.change_analysis import GitHubRepositoryProvider
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)


class ChangeAnalysisScheduler:
    _processor: ChangeAnalysisProcessor
    _clock: Clock
    _running: bool = False
    _task: Optional[asyncio.Task] = None

    def __init__(
        self,
        storage: StorageProvider,
        github_provider: GitHubRepositoryProvider,
        analysis_provider: AnalysisProvider,
        observations_provider: ObservationsProvider,
        clock: Clock = RealClock(),
    ):
        self._processor = ChangeAnalysisProcessor(
            storage=storage,
            github_provider=github_provider,
            analysis_provider=analysis_provider,
            observations_provider=observations_provider,
            clock=clock,
        )
        self._clock = clock

    async def start(self):
        if self._running:
            _log.warning("Change analysis scheduler is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        _log.info("Change analysis scheduler started")

    async def stop(self):
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        _log.info("Change analysis scheduler stopped")

    async def run_analysis_now(self):
        """Run analysis immediately (useful for testing or manual triggers)"""
        _log.info("Running change analysis immediately")
        try:
            await self._processor.run_daily_analysis()
        except Exception as e:
            _log.error(s_("Failed to run immediate analysis"), exc_info=e)
            raise

    async def _scheduler_loop(self):
        """Main scheduler loop that runs daily at a specific time"""
        try:
            while self._running:
                now = self._clock.now()
                next_run = self._calculate_next_run_time(now)
                
                _log.info(s_("Next change analysis scheduled", next_run=next_run.isoformat()))
                
                # Wait until the next scheduled time
                wait_seconds = (next_run - now).total_seconds()
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                
                if not self._running:
                    break
                
                # Run the analysis
                try:
                    _log.info("Starting scheduled change analysis")
                    await self._processor.run_daily_analysis()
                    _log.info("Completed scheduled change analysis")
                except Exception as e:
                    _log.error(s_("Failed during scheduled analysis"), exc_info=e)
                
                # Sleep for a minute to avoid running multiple times
                await asyncio.sleep(60)
                
        except asyncio.CancelledError:
            _log.info("Change analysis scheduler cancelled")
            raise
        except Exception as e:
            _log.error(s_("Scheduler loop failed"), exc_info=e)
            raise

    def _calculate_next_run_time(self, current_time: datetime) -> datetime:
        """Calculate the next time to run the analysis (daily at 2 AM UTC)"""
        target_time = time(2, 0)  # 2 AM UTC
        
        # Get today's target time
        today_target = current_time.replace(
            hour=target_time.hour,
            minute=target_time.minute,
            second=0,
            microsecond=0
        )
        
        # If we've already passed today's target time, schedule for tomorrow
        if current_time >= today_target:
            return today_target + timedelta(days=1)
        else:
            return today_target