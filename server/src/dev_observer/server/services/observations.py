import logging

from fastapi import APIRouter

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.web.observations_pb2 import GetObservationResponse, GetObservationsResponse, GetChangeSummariesRequest, GetChangeSummariesResponse, ChangeSummary
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import Clock, RealClock, pb_to_dict

_log = logging.getLogger(__name__)


class ObservationsService:
    _observations: ObservationsProvider
    _storage: StorageProvider
    _clock: Clock

    router: APIRouter

    def __init__(self, observations: ObservationsProvider, storage: StorageProvider, clock: Clock = RealClock()):
        self._observations = observations
        self._storage = storage
        self._clock = clock
        self.router = APIRouter()

        self.router.add_api_route("/observations/kind/{kind}", self.list_by_kind, methods=["GET"])
        self.router.add_api_route("/observation/{kind}/{name}/{key}", self.get, methods=["GET"])
        self.router.add_api_route("/change-summaries", self.get_change_summaries, methods=["POST"])

    async def list_by_kind(self, kind: str):
        keys = await self._observations.list(kind=kind)
        return pb_to_dict(GetObservationsResponse(keys=keys))

    async def get(self, kind: str, name: str, key: str):
        _log.debug(s_("Observation requested", kind=kind, name=name, key=key))
        observation = await self._observations.get(ObservationKey(kind=kind, name=name, key=key.replace("|", "/")))
        return pb_to_dict(GetObservationResponse(observation=observation))

    async def get_change_summaries(self, req: GetChangeSummariesRequest):
        """Get change summaries with optional filtering."""
        _log.debug(s_("Change summaries requested", request=req))
        
        # Get analysis jobs with filters
        jobs = await self._storage.get_change_analysis_jobs(
            repo_id=req.repo_id if req.HasField("repo_id") else None,
            status=req.status if req.HasField("status") else None
        )
        
        # Convert to ChangeSummary protos
        summaries = []
        for job in jobs:
            # Get repo name
            repo = await self._storage.get_github_repo(job.repo_id)
            repo_name = repo.full_name if repo else job.repo_id
            
            # Get summary content if available
            summary_content = None
            if job.observation_key and job.status.value == "completed":
                try:
                    observation = await self._observations.get(ObservationKey(
                        kind="change_summary",
                        name=repo_name,
                        key=job.observation_key
                    ))
                    summary_content = observation.content
                except Exception as e:
                    _log.warning(s_("Failed to get summary content", job_id=job.id), exc_info=e)
            
            summary = ChangeSummary(
                job_id=job.id,
                repo_id=job.repo_id,
                repo_name=repo_name,
                status=job.status.value,
                observation_key=job.observation_key,
                error_message=job.error_message,
                analyzed_at=job.analyzed_at.isoformat() if job.analyzed_at else None,
                summary_content=summary_content
            )
            summaries.append(summary)
        
        return pb_to_dict(GetChangeSummariesResponse(summaries=summaries))
