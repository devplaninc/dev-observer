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
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey
from dev_observer.api.types.repo_pb2 import GitHubRepository, GitProperties
from dev_observer.api.types.sites_pb2 import WebSite
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

    async def get_github_repo_by_full_name(self, full_name: str) -> Optional[GitHubRepository]:
        for r in self._get().github_repos:
            if r.full_name == full_name:
                return r
        return None

    async def delete_github_repo(self, repo_id: str):
        def up(d: LocalStorageData):
            new_repos = [r for r in d.github_repos if r.id != repo_id]
            d.ClearField("github_repos")
            d.github_repos.extend(new_repos)

        await self._update(up)

    async def add_github_repo(self, repo: GitHubRepository) -> GitHubRepository:
        if not repo.id or len(repo.id) == 0:
            repo.id = f"{uuid.uuid4()}"

        def up(d: LocalStorageData):
            if repo.id in [r.id for r in self._get().github_repos]:
                return
            d.github_repos.append(repo)
            if repo.id not in [i.key.github_repo_id for i in self._get().processing_items]:
                d.processing_items.append(ProcessingItem(
                    key=ProcessingItemKey(github_repo_id=repo.id),
                    next_processing=self._clock.now(),
                ))

        await self._update(up)
        return repo

    async def update_repo_properties(self, id: str, properties: GitProperties) -> GitHubRepository:
        def up(d: LocalStorageData):
            for r in d.github_repos:
                if r.id == id:
                    r.properties.CopyFrom(properties)
                    return
            raise ValueError(f"Repository with id {id} not found")

        await self._update(up)
        return await self.get_github_repo(id)

    async def get_web_sites(self) -> MutableSequence[WebSite]:
        return self._get().web_sites

    async def get_web_site(self, site_id: str) -> Optional[WebSite]:
        for s in self._get().web_sites:
            if s.id == site_id:
                return s
        return None

    async def delete_web_site(self, site_id: str):
        def up(d: LocalStorageData):
            new_sites = [s for s in d.web_sites if s.id != site_id]
            d.ClearField("web_sites")
            d.web_sites.extend(new_sites)

        await self._update(up)

    async def add_web_site(self, site: WebSite) -> WebSite:
        if not site.id or len(site.id) == 0:
            site.id = f"{uuid.uuid4()}"

        def up(d: LocalStorageData):
            if site.url in [s.url for s in self._get().web_sites]:
                return
            d.web_sites.append(site)
            if site.url not in [i.key.website_url for i in self._get().processing_items]:
                d.processing_items.append(ProcessingItem(
                    key=ProcessingItemKey(website_url=site.url),
                    next_processing=self._clock.now(),
                ))

        await self._update(up)
        return site

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        now = self._clock.now()
        items = [i for i in self._get().processing_items if
                 i.HasField("next_processing") and timestamp.to_datetime(i.next_processing,
                                                                         tz=datetime.timezone.utc) < now]
        if len(items) == 0:
            return None
        items.sort(key=lambda item: timestamp.to_datetime(item.next_processing))
        return items[0]

    async def get_processing_items(self) -> MutableSequence[ProcessingItem]:
        return self._get().processing_items

    async def get_processing_item(self, key: ProcessingItemKey) -> Optional[ProcessingItem]:
        for i in self._get().processing_items:
            if i.key == key:
                return i
        return None

    async def set_next_processing_time(self, key: ProcessingItemKey, next_time: Optional[datetime.datetime]):
        def up(d: LocalStorageData):
            found = False
            for i in d.processing_items:
                if i.key == key:
                    found = True
                    if next_time is None:
                        i.ClearField("next_processing")
                    else:
                        i.next_processing.CopyFrom(timestamp.from_milliseconds(int(next_time.timestamp() * 1000)))

            if not found:
                d.processing_items.append(ProcessingItem(key=key, next_processing=next_time))

        await self._update(up)

    async def upsert_processing_item(self, item: ProcessingItem):
        def up(d: LocalStorageData):
            if item.key in [i.key for i in d.processing_items]:
                new_items = [item if i.key == item.key else i for i in d.processing_items]
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
