import logging
from typing import Optional

from fastapi import APIRouter
from starlette.requests import Request

from dev_observer.api.web.changes_pb2 import (
    ListChangesSummariesRequest, ListChangesSummariesResponse,
    GetChangesSummaryRequest, GetChangesSummaryResponse,
    CreateChangesSummaryRequest, CreateChangesSummaryResponse,
    DeleteChangesSummaryRequest, DeleteChangesSummaryResponse
)
from dev_observer.api.types.changes_pb2 import GitHubChangesSummary
from dev_observer.log import s_
from dev_observer.processors.changes_summary import ChangesSummaryProcessor
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import parse_dict_pb, pb_to_dict

_log = logging.getLogger(__name__)


class ChangesSummaryService:
    _store: StorageProvider
    _processor: ChangesSummaryProcessor
    router: APIRouter

    def __init__(self, store: StorageProvider, processor: ChangesSummaryProcessor):
        self._store = store
        self._processor = processor
        self.router = APIRouter()

        self.router.add_api_route("/changes-summaries", self.list, methods=["GET"])
        self.router.add_api_route("/changes-summaries", self.create, methods=["POST"])
        self.router.add_api_route("/changes-summaries/{summary_id}", self.get, methods=["GET"])
        self.router.add_api_route("/changes-summaries/{summary_id}", self.delete, methods=["DELETE"])

    async def list(self, repo_id: str, limit: int = 50, offset: int = 0):
        """List changes summaries for a repository"""
        _log.debug(s_("Listing changes summaries", repo_id=repo_id, limit=limit, offset=offset))
        
        summaries = await self._store.list_changes_summaries(repo_id, limit, offset)
        
        return pb_to_dict(ListChangesSummariesResponse(
            summaries=summaries,
            total_count=len(summaries)  # TODO: Add proper count query
        ))

    async def get(self, summary_id: str):
        """Get a specific changes summary"""
        _log.debug(s_("Getting changes summary", summary_id=summary_id))
        
        summary = await self._store.get_changes_summary(summary_id)
        if not summary:
            return {"error": "Changes summary not found"}, 404
        
        return pb_to_dict(GetChangesSummaryResponse(summary=summary))

    async def create(self, req: Request):
        """Create a new changes summary"""
        request = parse_dict_pb(await req.json(), CreateChangesSummaryRequest())
        _log.debug(s_("Creating changes summary", request=request))
        
        # Get the repository
        repo = await self._store.get_github_repo(request.repo_id)
        if not repo:
            return {"error": "Repository not found"}, 404
        
        # Create the changes summary
        summary = await self._processor.create_changes_summary(
            repo, 
            days_back=request.days_back or 7
        )
        
        return pb_to_dict(CreateChangesSummaryResponse(summary=summary))

    async def delete(self, summary_id: str):
        """Delete a changes summary"""
        _log.debug(s_("Deleting changes summary", summary_id=summary_id))
        
        await self._store.delete_changes_summary(summary_id)
        
        return pb_to_dict(DeleteChangesSummaryResponse(success=True)) 