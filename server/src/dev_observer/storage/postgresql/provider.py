import datetime
from typing import Optional, MutableSequence

from google.protobuf import json_format
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey
from dev_observer.api.types.repo_pb2 import GitHubRepository
from dev_observer.storage.postgresql.model import GitRepoEntity, ProcessingItemEntity, GlobalConfigEntity
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import parse_json_pb, pb_to_json, Clock, RealClock


class PostgresqlStorageProvider(StorageProvider):
    _engine: AsyncEngine
    _clock: Clock

    def __init__(self, url: str, echo: bool = False, clock: Clock = RealClock()):
        self._engine = create_async_engine(url, echo=echo)
        self._clock = clock

    async def get_github_repos(self) -> MutableSequence[GitHubRepository]:
        async with AsyncSession(self._engine) as session:
            entities = await session.execute(select(GitRepoEntity))
            return [_to_repo(e[0]) for e in entities.all()]

    async def get_github_repo(self, repo_id: str) -> Optional[GitHubRepository]:
        async with AsyncSession(self._engine) as session:
            return _to_optional_repo(await session.get(GitRepoEntity, repo_id))

    async def delete_github_repo(self, repo_id: str):
        async with AsyncSession(self._engine) as session:
            await session.execute(delete(GitRepoEntity).where(GitRepoEntity.id == repo_id))

    async def add_github_repo(self, repo: GitHubRepository) -> GitHubRepository:
        async with AsyncSession(self._engine) as session:
            ent = GitRepoEntity(json_data=pb_to_json(repo))
            session.add(ent)
        return await self.get_github_repo(ent.id)

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        async with AsyncSession(self._engine) as session:
            res = await session.execute(
                select(ProcessingItemEntity)
                .where(
                    ProcessingItemEntity.next_processing != None,
                    ProcessingItemEntity.next_processing < self._clock.now(),
                )
                .order_by(ProcessingItemEntity.next_processing)
            )
            item = res.first()
        return _to_optional_item(item)

    async def set_next_processing_time(self, key: ProcessingItemKey, next_time: Optional[datetime.datetime]):
        key_str = json_format.MessageToJson(key, indent=None, sort_keys=True)
        async with AsyncSession(self._engine) as session:
            await session.execute(
                update(ProcessingItemEntity)
                .where(ProcessingItemEntity.key == key_str)
                .values(next_processing=next_time)
            )

    async def get_global_config(self) -> GlobalConfig:
        async with AsyncSession(self._engine) as session:
            ent = await session.get(GlobalConfigEntity, "global_config")
            return parse_json_pb(ent.json_data, GlobalConfig())

    async def set_global_config(self, config: GlobalConfig) -> GlobalConfig:
        async with AsyncSession(self._engine) as session:
            await session.execute(
                update(GlobalConfigEntity)
                .where(GlobalConfigEntity.id=="global_config")
                .values(json_data=pb_to_json(config))
            )
        return await self.get_global_config()


def _to_optional_repo(ent: Optional[GitRepoEntity]) -> Optional[GitHubRepository]:
    return None if ent is None else parse_json_pb(ent.json_data, GitHubRepository())


def _to_repo(ent: GitRepoEntity) -> GitHubRepository:
    data = parse_json_pb(ent.json_data, GitHubRepository())
    data.id = ent.id
    return data


def _to_optional_item(ent: Optional[ProcessingItemEntity]) -> Optional[ProcessingItem]:
    return None if ent is None else _to_item(ent)


def _to_item(ent: ProcessingItemEntity) -> ProcessingItem:
    data = parse_json_pb(ent.json_data, ProcessingItem())
    data.next_processing = ent.next_processing
    data.last_processed = ent.last_processed
    data.last_error = ent.last_error
    data.no_processing = ent.no_processing
    data.key = parse_json_pb(ent.key, ProcessingItemKey())
    return data
