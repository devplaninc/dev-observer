import abc
import asyncio
import datetime
import logging
import uuid
from abc import abstractmethod
from typing import Optional, Callable, MutableSequence

from google.protobuf import timestamp

from dev_observer.api.storage.local_pb2 import LocalStorageData
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem
from dev_observer.api.types.repo_pb2 import GitHubRepository
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock

_log = logging.getLogger(__name__)

_lock = asyncio.Lock()


class SingleBlobStorageProvider(abc.ABC, StorageProvider):
    _clock: Clock

    def __init__(self, clock: Clock = RealClock()):
        self._clock = clock

    async def get_github_repos(self) -> MutableSequence[GitHubRepository]:
        return self._get().github_repos

    async def get_github_repo(self, repo_id: str) -> Optional[GitHubRepository]:
        for r in self._get().github_repos:
            if r.id == repo_id:
                return r
        return None

    async def add_github_repo(self, repo: GitHubRepository) -> MutableSequence[GitHubRepository]:
        def up(d: LocalStorageData):
            if repo.id in [r.id for r in self._get().github_repos]:
                return
            d.github_repos.append(repo)
            if repo.id not in [i.github_repo_id for i in self._get().processing_items]:
                d.processing_items.append(ProcessingItem(
                    id=f"{uuid.uuid4()}",
                    github_repo_id=repo.id,
                    next_processing=self._clock.now(),
                ))

        data = await self._update(up)
        return data.github_repos

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        now = self._clock.now()
        items = [i for i in self._get().processing_items if
                 i.HasField("next_processing") and timestamp.to_datetime(i.next_processing, tz=datetime.timezone.utc) < now]
        if len(items) == 0:
            return None
        items.sort(key=lambda item: timestamp.to_datetime(item.next_processing))
        return items[0]

    async def get_processing_items(self) -> MutableSequence[ProcessingItem]:
        return self._get().processing_items

    async def set_next_processing_time(self, item_id: str, next_time: Optional[datetime.datetime]):
        def up(d: LocalStorageData):
            for i in d.processing_items:
                if i.id == item_id:
                    if next_time is None:
                        i.ClearField("next_processing")
                    else:
                        i.next_processing.CopyFrom(timestamp.from_milliseconds(int(next_time.timestamp() * 1000)))

        await self._update(up)

    async def upsert_processing_item(self, item: ProcessingItem):
        def up(d: LocalStorageData):
            if item.id in [i.id for i in d.processing_items]:
                new_items = [item if i.id == item.id else i for i in d.processing_items]
                d.processing_items.clear()
                d.processing_items.extend(new_items)
            else:
                d.processing_items.append(item)

        await self._update(up)

    async def get_global_config(self) -> GlobalConfig:
        return self._get().global_config

    async def set_global_config(self, config: GlobalConfig) -> GlobalConfig:
        def up(d: LocalStorageData):
            d.global_config.CopyFrom(config)

        data = await self._update(up)
        return data.global_config

    async def _update(self, updater: Callable[[LocalStorageData], None]) -> LocalStorageData:
        async with _lock:
            data = self._get()
            updater(data)
            self._store(data)
            return self._get()

    @abstractmethod
    def _get(self) -> LocalStorageData:
        ...

    @abstractmethod
    def _store(self, data: LocalStorageData):
        ...
