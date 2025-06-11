import datetime
from typing import Protocol, Optional, MutableSequence

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey
from dev_observer.api.types.repo_pb2 import GitHubRepository


class StorageProvider(Protocol):
    async def get_github_repos(self) -> MutableSequence[GitHubRepository]:
        ...

    async def get_github_repo(self, repo_id: str) -> Optional[GitHubRepository]:
        ...

    async def get_github_repo_by_full_name(self, full_name: str) -> Optional[GitHubRepository]:
        ...

    async def delete_github_repo(self, repo_id: str):
        ...

    async def add_github_repo(self, repo: GitHubRepository) -> GitHubRepository:
        ...

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        ...

    async def set_next_processing_time(self, key: ProcessingItemKey, next_time: Optional[datetime.datetime]):
        ...

    async def get_global_config(self) -> GlobalConfig:
        ...

    async def set_global_config(self, config: GlobalConfig) -> GlobalConfig:
        ...
