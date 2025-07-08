import datetime
import uuid
from typing import Optional, MutableSequence

from google.protobuf import json_format
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey
from dev_observer.api.types.repo_pb2 import GitHubRepository, GitProperties, GitHubChangeSummary
from dev_observer.api.types.sites_pb2 import WebSite
from dev_observer.storage.postgresql.model import GitRepoEntity, ProcessingItemEntity, GlobalConfigEntity, WebsiteEntity, GitHubChangeSummaryEntity
from dev_observer.storage.provider import StorageProvider, AddWebSiteData
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

    async def add_web_site(self, site: WebSite) -> AddWebSiteData:
        site_id = site.id
        if not site_id or len(site_id) == 0:
            site_id = f"{uuid.uuid4()}"
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                existing = await session.scalar(
                    select(WebsiteEntity).where(WebsiteEntity.url == site.url)
                )
                if existing is not None:
                    return AddWebSiteData(_to_web_site(existing), created=False)
                s = WebsiteEntity(
                    id=site_id,
                    url=site.url,
                    json_data=pb_to_json(site),
                )
                session.add(s)
                return AddWebSiteData(
                    _to_optional_web_site(await session.get(WebsiteEntity, site_id)),
                    created=True,
                )

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

    async def add_github_change_summary(self, summary: GitHubChangeSummary) -> GitHubChangeSummary:
        summary_id = summary.id
        if not summary_id or len(summary_id) == 0:
            summary_id = f"{uuid.uuid4()}"
        async with AsyncSession(self._engine) as session:
            async with session.begin():
                entity = GitHubChangeSummaryEntity(
                    id=summary_id,
                    repo_id=summary.repo_id,
                    commit_sha=summary.commit_sha,
                    analysis_type=summary.analysis_type,
                    summary=summary.summary,
                    changes_data=summary.changes_data,
                    analysis_period_start=summary.analysis_period_start.ToDatetime(),
                    analysis_period_end=summary.analysis_period_end.ToDatetime(),
                )
                session.add(entity)
                return _to_optional_github_change_summary(await session.get(GitHubChangeSummaryEntity, summary_id))

    async def get_github_change_summaries(self, repo_id: str, analysis_type: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> tuple[MutableSequence[GitHubChangeSummary], int]:
        async with AsyncSession(self._engine) as session:
            query = select(GitHubChangeSummaryEntity).where(GitHubChangeSummaryEntity.repo_id == repo_id)
            if analysis_type:
                query = query.where(GitHubChangeSummaryEntity.analysis_type == analysis_type)
            
            count_query = query.with_only_columns(GitHubChangeSummaryEntity.id)
            total_count = len((await session.execute(count_query)).all())
            
            query = query.order_by(GitHubChangeSummaryEntity.created_at.desc())
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            entities = await session.execute(query)
            return [_to_github_change_summary(e[0]) for e in entities.all()], total_count

    async def get_github_change_summary(self, summary_id: str) -> Optional[GitHubChangeSummary]:
        async with AsyncSession(self._engine) as session:
            return _to_optional_github_change_summary(await session.get(GitHubChangeSummaryEntity, summary_id))


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


def _to_optional_github_change_summary(ent: Optional[GitHubChangeSummaryEntity]) -> Optional[GitHubChangeSummary]:
    return None if ent is None else _to_github_change_summary(ent)


def _to_github_change_summary(ent: GitHubChangeSummaryEntity) -> GitHubChangeSummary:
    summary = GitHubChangeSummary()
    summary.id = ent.id
    summary.repo_id = ent.repo_id
    summary.commit_sha = ent.commit_sha
    summary.analysis_type = ent.analysis_type
    summary.summary = ent.summary
    summary.changes_data = ent.changes_data
    summary.analysis_period_start.FromDatetime(ent.analysis_period_start)
    summary.analysis_period_end.FromDatetime(ent.analysis_period_end)
    summary.created_at.FromDatetime(ent.created_at)
    summary.updated_at.FromDatetime(ent.updated_at)
    return summary
