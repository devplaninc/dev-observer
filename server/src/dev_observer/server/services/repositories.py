import logging

from fastapi import APIRouter
from starlette.requests import Request

from dev_observer.api.types.processing_pb2 import ProcessingItemKey
from dev_observer.api.web.repositories_pb2 import AddGithubRepositoryRequest, AddGithubRepositoryResponse, \
    ListGithubRepositoriesResponse, RescanRepositoryResponse
from dev_observer.log import s_
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import parse_dict_pb, pb_to_json, Clock, RealClock

_log = logging.getLogger(__name__)


class RepositoriesService:
    _store: StorageProvider
    _clock: Clock

    router: APIRouter

    def __init__(self, store: StorageProvider, clock: Clock = RealClock()):
        self._store = store
        self._clock = clock
        self.router = APIRouter()

        self.router.add_api_route("/repositories", self.add_github_repo, methods=["POST"])
        self.router.add_api_route("/repositories", self.list, methods=["GET"])
        self.router.add_api_route("/repositories/{repo_id}/rescan", self.rescan, methods=["POST"])


    async def add_github_repo(self, req: Request):
        request = parse_dict_pb(await req.json(), AddGithubRepositoryRequest())
        _log.debug(s_("Adding repository", request=request))
        await self._store.add_github_repo(request.repo)
        return pb_to_json(AddGithubRepositoryResponse())

    async def list(self):
        repos = await self._store.get_github_repos()
        return pb_to_json(ListGithubRepositoriesResponse(repos=repos))

    async def rescan(self, repo_id: str):
        await self._store.set_next_processing_time(
            ProcessingItemKey(github_repo_id=repo_id), self._clock.now(),
        )
        return pb_to_json(RescanRepositoryResponse())