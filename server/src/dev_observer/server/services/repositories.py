import logging
from typing import Optional

from fastapi import APIRouter
from starlette.requests import Request

from dev_observer.api.types.processing_pb2 import ProcessingItemKey
from dev_observer.api.types.repo_pb2 import GitHubRepository
from dev_observer.api.web.repositories_pb2 import AddGithubRepositoryRequest, AddGithubRepositoryResponse, \
    ListGithubRepositoriesResponse, RescanRepositoryResponse, GetRepositoryResponse, DeleteRepositoryResponse, \
    EnrollRepositoryForChangeAnalysisRequest, EnrollRepositoryForChangeAnalysisResponse, \
    UnenrollRepositoryFromChangeAnalysisRequest, UnenrollRepositoryFromChangeAnalysisResponse, \
    GetChangeAnalysesRequest, GetChangeAnalysesResponse, \
    GetChangeAnalysisRequest, GetChangeAnalysisResponse
from dev_observer.analytics.provider import ChangeAnalysisAnalytics
from dev_observer.log import s_
from dev_observer.repository.parser import parse_github_url
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import parse_dict_pb, Clock, RealClock, pb_to_dict

_log = logging.getLogger(__name__)


class RepositoriesService:
    _store: StorageProvider
    _analytics: Optional[ChangeAnalysisAnalytics]
    _clock: Clock

    router: APIRouter

    def __init__(self, store: StorageProvider, analytics: Optional[ChangeAnalysisAnalytics] = None, clock: Clock = RealClock()):
        self._store = store
        self._analytics = analytics
        self._clock = clock
        self.router = APIRouter()

        self.router.add_api_route("/repositories", self.add_github_repo, methods=["POST"])
        self.router.add_api_route("/repositories", self.list, methods=["GET"])
        self.router.add_api_route("/repositories/{repo_id}", self.get, methods=["GET"])
        self.router.add_api_route("/repositories/{repo_id}", self.delete, methods=["DELETE"])
        self.router.add_api_route("/repositories/{repo_id}/rescan", self.rescan, methods=["POST"])
        
        # Change analysis endpoints
        self.router.add_api_route("/repositories/{repo_id}/change-analysis/enroll", self.enroll_for_change_analysis, methods=["POST"])
        self.router.add_api_route("/repositories/{repo_id}/change-analysis/unenroll", self.unenroll_from_change_analysis, methods=["POST"])
        self.router.add_api_route("/repositories/{repo_id}/change-analyses", self.get_change_analyses, methods=["GET"])
        self.router.add_api_route("/change-analyses/{analysis_id}", self.get_change_analysis, methods=["GET"])

    async def add_github_repo(self, req: Request):
        request = parse_dict_pb(await req.json(), AddGithubRepositoryRequest())
        _log.debug(s_("Adding repository", request=request))
        parsed_url = parse_github_url(request.url)
        repo = await self._store.add_github_repo(GitHubRepository(
            full_name=parsed_url.get_full_name(),
            name=parsed_url.name,
            url=request.url,
        ))
        return pb_to_dict(AddGithubRepositoryResponse(repo=repo))

    async def get(self, repo_id: str):
        repo = await self._store.get_github_repo(repo_id)
        return pb_to_dict(GetRepositoryResponse(repo=repo))

    async def delete(self, repo_id: str):
        await self._store.delete_github_repo(repo_id)
        repos = await self._store.get_github_repos()
        return pb_to_dict(DeleteRepositoryResponse(repos=repos))

    async def list(self):
        repos = await self._store.get_github_repos()
        return pb_to_dict(ListGithubRepositoriesResponse(repos=repos))

    async def rescan(self, repo_id: str):
        await self._store.set_next_processing_time(
            ProcessingItemKey(github_repo_id=repo_id), self._clock.now(),
        )
        return pb_to_dict(RescanRepositoryResponse())

    async def enroll_for_change_analysis(self, req: Request, repo_id: str):
        _log.debug(s_("Enrolling repository for change analysis", repo_id=repo_id))
        repo = await self._store.enroll_repo_for_change_analysis(repo_id)
        
        # Track enrollment
        if self._analytics:
            await self._analytics.track_enrollment(repo_id, repo.full_name)
        
        return pb_to_dict(EnrollRepositoryForChangeAnalysisResponse(repo=repo))

    async def unenroll_from_change_analysis(self, req: Request, repo_id: str):
        _log.debug(s_("Unenrolling repository from change analysis", repo_id=repo_id))
        repo = await self._store.unenroll_repo_from_change_analysis(repo_id)
        
        # Track unenrollment
        if self._analytics:
            await self._analytics.track_unenrollment(repo_id, repo.full_name)
        
        return pb_to_dict(UnenrollRepositoryFromChangeAnalysisResponse(repo=repo))

    async def get_change_analyses(self, repo_id: str, date_from: str = None, date_to: str = None, status: str = None):
        from datetime import datetime
        
        _log.debug(s_("Getting change analyses", repo_id=repo_id, date_from=date_from, date_to=date_to, status=status))
        
        # Track API access
        if self._analytics:
            await self._analytics.track_api_access("get_change_analyses", repo_id, filters={
                "date_from": date_from,
                "date_to": date_to, 
                "status": status
            })
        
        # Get all analyses for the repository
        analyses = await self._store.get_repo_change_analyses_by_repo(repo_id)
        
        # Apply filters
        filtered_analyses = []
        for analysis in analyses:
            # Filter by status
            if status and analysis.status != status:
                continue
            
            # Filter by date range
            if date_from or date_to:
                if not analysis.HasField("analyzed_at"):
                    continue
                
                analysis_date = analysis.analyzed_at.ToDatetime()
                
                if date_from:
                    try:
                        from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                        if analysis_date < from_date:
                            continue
                    except ValueError:
                        _log.warning(s_("Invalid date_from format", date_from=date_from))
                
                if date_to:
                    try:
                        to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                        if analysis_date > to_date:
                            continue
                    except ValueError:
                        _log.warning(s_("Invalid date_to format", date_to=date_to))
            
            filtered_analyses.append(analysis)
        
        return pb_to_dict(GetChangeAnalysesResponse(analyses=filtered_analyses))

    async def get_change_analysis(self, analysis_id: str):
        _log.debug(s_("Getting change analysis", analysis_id=analysis_id))
        analysis = await self._store.get_repo_change_analysis(analysis_id)
        return pb_to_dict(GetChangeAnalysisResponse(analysis=analysis))
