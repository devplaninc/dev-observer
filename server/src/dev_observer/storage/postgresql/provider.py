import datetime
import uuid
from typing import Optional, MutableSequence

from google.protobuf import json_format
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey
from dev_observer.api.types.repo_pb2 import GitHubRepository, GitProperties
from dev_observer.api.types.sites_pb2 import WebSite
from dev_observer.storage.postgresql.model import GitRepoEntity, ProcessingItemEntity, GlobalConfigEntity, WebsiteEntity
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

    async def get_github_repo_by_full_name(self, full_name: str) -> Optional[GitHubRepository]:
        async with AsyncSession(self._engine) as session:
            res = await session.execute(select(GitRepoEntity).where(GitRepoEntity.full_name == full_name))
            ent = res.first()
            return _to_optional_repo(ent[0] if ent is not None else None)

    async def delete_github_repo(self, repo_id: str):
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(delete(GitRepoEntity).where(GitRepoEntity.id == repo_id))

    async def add_github_repo(self, repo: GitHubRepository) -> GitHubRepository:
        repo_id = repo.id
        if not repo_id or len(repo_id) == 0:
            repo_id = f"{uuid.uuid4()}"
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.execute(
                    select(GitRepoEntity).where(GitRepoEntity.full_name == repo.full_name)
                )
                ent = existing.first()
                if ent is not None:
                    return _to_repo(ent[0])
                r = GitRepoEntity(
                    id=repo_id,
                    full_name=repo.full_name,
                    json_data=pb_to_json(repo),
                )
                session.add(r)
                return _to_optional_repo(await session.get(GitRepoEntity, repo_id))

    async def update_repo_properties(self, repo_id: str, properties: GitProperties) -> GitHubRepository:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.execute(
                    select(GitRepoEntity).where(GitRepoEntity.id == repo_id)
                )
                ent = existing.first()
                if ent is None:
                    raise ValueError(f"Repository with id {repo_id} not found")
                updated = _to_repo(ent[0])
                updated.properties.CopyFrom(properties)
                await session.execute(
                    update(GitRepoEntity)
                    .where(GitRepoEntity.id == repo_id)
                    .values(json_data=pb_to_json(updated))
                )
        return await self.get_github_repo(repo_id)

    async def get_web_sites(self) -> MutableSequence[WebSite]:
        async with AsyncSession(self._engine) as session:
            entities = await session.execute(select(WebsiteEntity))
            return [_to_web_site(e[0]) for e in entities.all()]

    async def get_web_site(self, site_id: str) -> Optional[WebSite]:
        async with AsyncSession(self._engine) as session:
            ent = await session.scalar(select(WebsiteEntity).where(WebsiteEntity.id == site_id))
            return _to_optional_web_site(ent)

    async def delete_web_site(self, site_id: str):
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(delete(WebsiteEntity).where(WebsiteEntity.id == site_id))

    async def add_web_site(self, site: WebSite) -> WebSite:
        site_id = site.id
        if not site_id or len(site_id) == 0:
            site_id = f"{uuid.uuid4()}"
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.scalar(
                    select(WebsiteEntity).where(WebsiteEntity.url == site.url)
                )
                if existing is not None:
                    return _to_web_site(existing)
                s = WebsiteEntity(
                    id=site_id,
                    url=site.url,
                    json_data=pb_to_json(site),
                )
                session.add(s)
                return _to_optional_web_site(await session.get(WebsiteEntity, site_id))

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        next_processing_time = self._clock.now()
        async with AsyncSession(self._engine) as session:
            res = await session.execute(
                select(ProcessingItemEntity)
                .where(
                    ProcessingItemEntity.next_processing != None,
                    ProcessingItemEntity.next_processing < next_processing_time,
                )
                .order_by(ProcessingItemEntity.next_processing)
            )
            item = res.first()
            return _to_optional_item(item[0] if item is not None else None)

    async def set_next_processing_time(self, key: ProcessingItemKey, next_time: Optional[datetime.datetime]):
        key_str = json_format.MessageToJson(key, indent=None, sort_keys=True)
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.get(ProcessingItemEntity, key_str)
                if existing is not None:
                    await session.execute(
                        update(ProcessingItemEntity)
                        .where(ProcessingItemEntity.key == key_str)
                        .values(next_processing=next_time)
                    )
                else:
                    session.add(ProcessingItemEntity(key=key_str, next_processing=next_time, json_data="{}"))

    async def get_global_config(self) -> GlobalConfig:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                all_configs = await session.execute(select(GlobalConfigEntity))
                ent = all_configs.first()
                if ent is None:
                    session.add(GlobalConfigEntity(id="global_config", json_data="{}"))
                    return GlobalConfig()
                return parse_json_pb(ent[0].json_data, GlobalConfig())

    async def set_global_config(self, config: GlobalConfig) -> GlobalConfig:
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                await session.execute(
                    update(GlobalConfigEntity)
                    .where(GlobalConfigEntity.id == "global_config")
                    .values(json_data=pb_to_json(config))
                )
        return await self.get_global_config()


def _to_optional_repo(ent: Optional[GitRepoEntity]) -> Optional[GitHubRepository]:
    return None if ent is None else _to_repo(ent)


def _to_repo(ent: GitRepoEntity) -> GitHubRepository:
    data = parse_json_pb(ent.json_data, GitHubRepository())
    data.id = ent.id
    return data


def _to_optional_web_site(ent: Optional[WebsiteEntity]) -> Optional[WebSite]:
    return None if ent is None else _to_web_site(ent)


def _to_web_site(ent: WebsiteEntity) -> WebSite:
    data = parse_json_pb(ent.json_data, WebSite())
    data.id = ent.id
    data.url = ent.url
    return data


def _to_optional_item(ent: Optional[ProcessingItemEntity]) -> Optional[ProcessingItem]:
    return None if ent is None else _to_item(ent)


def _to_item(ent: ProcessingItemEntity) -> ProcessingItem:
    data = parse_json_pb(ent.json_data, ProcessingItem())

    if ent.next_processing is None:
        data.ClearField("next_processing")
    else:
        data.next_processing = ent.next_processing

    if ent.last_processed is None:
        data.ClearField("last_processed")
    else:
        data.last_processed = ent.last_processed
    data.last_error = ent.last_error if ent.last_error else ""
    data.no_processing = ent.no_processing
    data.key.CopyFrom(parse_json_pb(ent.key, ProcessingItemKey()))
    return data
