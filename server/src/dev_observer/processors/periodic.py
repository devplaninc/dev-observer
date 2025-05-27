from datetime import timedelta
from typing import List, Optional

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.types.processing_pb2 import ProcessingItem
from dev_observer.processors.flattening import ObservationRequest
from dev_observer.processors.repos import ReposProcessor, ObservedRepo
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock


class PeriodicProcessor:
    _storage: StorageProvider
    _repos_processor: ReposProcessor
    _clock: Clock

    def __init__(self,
                 storage: StorageProvider,
                 repos_processor: ReposProcessor,
                 clock: Clock = RealClock(),
                 ):
        self._storage = storage
        self._repos_processor = repos_processor
        self._clock = clock

    async def process_next(self) -> Optional[ProcessingItem]:
        item = await self._storage.next_processing_item()
        if item is None:
            return None
        retry_time = self._clock.now() + timedelta(minutes=30)
        # prevent from running again right away.
        await self._storage.set_next_processing_time(item.id, retry_time)
        await self._process_item(item)
        return item

    async def _process_item(self, item: ProcessingItem):
        ent_type = item.WhichOneof("entity")
        if ent_type == "github_repo_id":
            await self._process_github_repo(item.github_repo_id)
        else:
            raise ValueError(f"[{ent_type}] is not supported")
        await self._storage.set_next_processing_time(item.id, None)

    async def _process_github_repo(self, repo_id: str):
        repo = await self._storage.get_github_repo(repo_id)
        if repo is None:
            raise ValueError(f"Repo with id [{repo_id}] is not found")
        requests: List[ObservationRequest] = []
        config = await self._storage.get_global_config()
        for analyzer in config.analysis.repo_analyzers:
            key = f"{repo.full_name}/{analyzer.file_name}"
            requests.append(ObservationRequest(
                prompt_prefix=analyzer.prompt_prefix,
                key=ObservationKey(kind="repos", name=analyzer.file_name, key=key),
            ))
        if len(requests) == 0:
            return
        await self._repos_processor.process(ObservedRepo(url=repo.url), requests)
