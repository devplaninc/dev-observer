import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from google.protobuf.timestamp_pb2 import Timestamp

from dev_observer.api.web.change_analysis_pb2 import (
    EnrollRepositoryRequest, EnrollRepositoryResponse,
    UnenrollRepositoryRequest, UnenrollRepositoryResponse,
    GetChangeSummariesRequest, GetChangeSummariesResponse,
    GetRepositoryEnrollmentStatusRequest, GetRepositoryEnrollmentStatusResponse,
    ChangeSummary
)
from dev_observer.api.types.repo_pb2 import ChangeAnalysisConfig, GitProperties
from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.storage.provider import StorageProvider
from dev_observer.storage.postgresql.model import RepoChangeAnalysisEntity
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.util import parse_dict_pb, pb_to_dict, Clock, RealClock
from dev_observer.log import s_

_log = logging.getLogger(__name__)


class ChangeAnalysisService:
    _store: StorageProvider
    _observations: Optional[ObservationsProvider]
    _clock: Clock

    router: APIRouter

    def __init__(self, store: StorageProvider, observations: Optional[ObservationsProvider] = None, clock: Clock = RealClock()):
        self._store = store
        self._observations = observations
        self._clock = clock
        self.router = APIRouter()

        self.router.add_api_route("/repositories/{repo_id}/change-analysis/enroll", self.enroll_repository, methods=["POST"])
        self.router.add_api_route("/repositories/{repo_id}/change-analysis/unenroll", self.unenroll_repository, methods=["POST"])
        self.router.add_api_route("/repositories/{repo_id}/change-analysis/status", self.get_enrollment_status, methods=["GET"])
        self.router.add_api_route("/change-summaries", self.get_change_summaries, methods=["GET"])

    async def enroll_repository(self, repo_id: str, req: Request):
        """Enroll a repository for change analysis."""
        try:
            _log.debug(s_("Enrolling repository for change analysis", repo_id=repo_id))

            # Get the repository
            repo = await self._store.get_github_repo(repo_id)
            if not repo:
                raise HTTPException(status_code=404, detail="Repository not found")

            # Update the repository's change analysis config
            properties = repo.properties if repo.properties else GitProperties()
            if not properties.change_analysis:
                properties.change_analysis = ChangeAnalysisConfig()

            properties.change_analysis.enrolled = True

            # Save the updated repository properties
            await self._store.update_repo_properties(repo_id, properties)

            return pb_to_dict(EnrollRepositoryResponse(success=True, message="Repository enrolled successfully"))

        except Exception as e:
            _log.error(s_("Failed to enroll repository", repo_id=repo_id, error=str(e)))
            return pb_to_dict(EnrollRepositoryResponse(success=False, message=f"Failed to enroll repository: {str(e)}"))

    async def unenroll_repository(self, repo_id: str, req: Request):
        """Unenroll a repository from change analysis."""
        try:
            _log.debug(s_("Unenrolling repository from change analysis", repo_id=repo_id))

            # Get the repository
            repo = await self._store.get_github_repo(repo_id)
            if not repo:
                raise HTTPException(status_code=404, detail="Repository not found")

            # Update the repository's change analysis config
            properties = repo.properties if repo.properties else GitProperties()
            if not properties.change_analysis:
                properties.change_analysis = ChangeAnalysisConfig()

            properties.change_analysis.enrolled = False

            # Save the updated repository properties
            await self._store.update_repo_properties(repo_id, properties)

            return pb_to_dict(UnenrollRepositoryResponse(success=True, message="Repository unenrolled successfully"))

        except Exception as e:
            _log.error(s_("Failed to unenroll repository", repo_id=repo_id, error=str(e)))
            return pb_to_dict(UnenrollRepositoryResponse(success=False, message=f"Failed to unenroll repository: {str(e)}"))

    async def get_enrollment_status(self, repo_id: str):
        """Get the enrollment status of a repository."""
        try:
            repo = await self._store.get_github_repo(repo_id)
            if not repo:
                raise HTTPException(status_code=404, detail="Repository not found")

            enrolled = False
            last_analysis = None

            if repo.properties and repo.properties.change_analysis:
                enrolled = repo.properties.change_analysis.enrolled
                if repo.properties.change_analysis.last_analysis:
                    last_analysis = repo.properties.change_analysis.last_analysis

            return pb_to_dict(GetRepositoryEnrollmentStatusResponse(
                enrolled=enrolled,
                last_analysis=last_analysis
            ))

        except Exception as e:
            _log.error(s_("Failed to get enrollment status", repo_id=repo_id, error=str(e)))
            raise HTTPException(status_code=500, detail=f"Failed to get enrollment status: {str(e)}")

    async def get_change_summaries(self, req: Request):
        """Get change summaries with optional filtering."""
        try:
            # Parse query parameters
            query_params = dict(req.query_params)
            request = GetChangeSummariesRequest()

            if 'repo_id' in query_params:
                request.repo_id = query_params['repo_id']
            if 'status' in query_params:
                request.status = query_params['status']

            # Parse date range parameters
            start_date = None
            end_date = None
            if 'start_date' in query_params:
                try:
                    start_date = datetime.fromisoformat(query_params['start_date'].replace('Z', '+00:00'))
                    timestamp = Timestamp()
                    timestamp.FromDatetime(start_date)
                    request.start_date.CopyFrom(timestamp)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"Invalid start_date format: {str(e)}")

            if 'end_date' in query_params:
                try:
                    end_date = datetime.fromisoformat(query_params['end_date'].replace('Z', '+00:00'))
                    timestamp = Timestamp()
                    timestamp.FromDatetime(end_date)
                    request.end_date.CopyFrom(timestamp)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=f"Invalid end_date format: {str(e)}")

            _log.debug(s_("Getting change summaries", request=request))

            # Get change analysis records from database
            summaries = await self._store.get_change_analysis_records(
                repo_id=request.repo_id if request.repo_id else None,
                status=request.status if request.status else None,
                start_date=start_date,
                end_date=end_date
            )

            # Convert to protobuf format
            pb_summaries = []
            for summary in summaries:
                pb_summary = ChangeSummary(
                    id=summary.id,
                    repo_id=summary.repo_id,
                    status=summary.status,
                    error_message=summary.error_message,
                    analyzed_at=summary.analyzed_at,
                    created_at=summary.created_at
                )

                # Get observation if available
                if summary.observation_key and self._observations:
                    try:
                        # Parse the observation key to create ObservationKey object
                        observation_key = ObservationKey(
                            kind="change_analysis",
                            name="daily_summary",
                            key=summary.observation_key
                        )
                        observation = await self._observations.get(observation_key)
                        pb_summary.observation.CopyFrom(observation)
                    except Exception as e:
                        _log.warning(s_("Failed to get observation", observation_key=summary.observation_key, error=str(e)))

                pb_summaries.append(pb_summary)

            return pb_to_dict(GetChangeSummariesResponse(summaries=pb_summaries))

        except Exception as e:
            _log.error(s_("Failed to get change summaries", error=str(e)))
            raise HTTPException(status_code=500, detail=f"Failed to get change summaries: {str(e)}")
