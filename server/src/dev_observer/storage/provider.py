import dataclasses
import datetime
from typing import Protocol, Optional, MutableSequence, List

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.api.types.processing_pb2 import ProcessingItem, ProcessingItemKey
from dev_observer.api.types.repo_pb2 import GitHubRepository, GitProperties
from dev_observer.api.types.sites_pb2 import WebSite
from dev_observer.storage.postgresql.model import RepoChangeAnalysisEntity

@dataclasses.dataclass
class AddWebSiteData:
    site: WebSite
    created: bool


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

    async def update_repo_properties(self, id: str, properties: GitProperties) -> GitHubRepository:
        ...

    async def update_github_repo(self, repo: GitHubRepository) -> GitHubRepository:
        ...


    async def get_web_sites(self) -> MutableSequence[WebSite]:
        ...

    async def get_web_site(self, site_id: str) -> Optional[WebSite]:
        ...

    async def delete_web_site(self, site_id: str):
        ...

    async def add_web_site(self, site: WebSite) -> AddWebSiteData:
        ...

    async def next_processing_item(self) -> Optional[ProcessingItem]:
        ...

    async def set_next_processing_time(self, key: ProcessingItemKey, next_time: Optional[datetime.datetime]):
        ...

    async def get_global_config(self) -> GlobalConfig:
        ...

    async def set_global_config(self, config: GlobalConfig) -> GlobalConfig:
        ...

    # Change Analysis methods
    async def get_change_analysis_jobs(self, repo_id: Optional[str] = None, status: Optional[str] = None) -> List[RepoChangeAnalysisEntity]:
        ...

    async def get_change_analysis_job(self, job_id: str) -> Optional[RepoChangeAnalysisEntity]:
        ...

    async def create_change_analysis_job(self, job: RepoChangeAnalysisEntity) -> RepoChangeAnalysisEntity:
        ...

    async def update_change_analysis_job(self, job: RepoChangeAnalysisEntity) -> RepoChangeAnalysisEntity:
        ...

    async def get_today_analysis_job(self, repo_id: str, date: datetime.date) -> Optional[RepoChangeAnalysisEntity]:
        ...
