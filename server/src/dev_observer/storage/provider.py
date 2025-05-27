import datetime
from typing import Protocol, Optional, MutableSequence

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem
from dev_observer.api.types.repo_pb2 import GitHubRepository


class StorageProvider(Protocol):
    async def get_github_repos(self) -> MutableSequence[GitHubRepository]:
        ...

    async def get_github_repo(self, repo_id: str) -> Optional[GitHubRepository]:
        ...

    async def add_github_repo(self, repo: GitHubRepository) -> MutableSequence[GitHubRepository]:
        ...

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        ...

    async def get_processing_items(self) -> MutableSequence[ProcessingItem]:
        ...

    async def set_next_processing_time(self, item_id: str, next_time: Optional[datetime.datetime]):
        ...

    async def upsert_processing_item(self, item: ProcessingItem):
        ...

    async def get_global_config(self) -> GlobalConfig:
        ...

    async def set_global_config(self, config: GlobalConfig) -> GlobalConfig:
        ...
