import logging

from fastapi import APIRouter

from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.api.web.observations_pb2 import GetObservationResponse, GetObservationsResponse
from dev_observer.log import s_
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.util import Clock, RealClock, pb_to_dict

_log = logging.getLogger(__name__)


class ObservationsService:
    _observations: ObservationsProvider
    _clock: Clock

    router: APIRouter

    def __init__(self, observations: ObservationsProvider, clock: Clock = RealClock()):
        self._observations = observations
        self._clock = clock
        self.router = APIRouter()

        self.router.add_api_route("/observations/kind/{kind}", self.list_by_kind, methods=["GET"])
        self.router.add_api_route("/observation/{kind}/{name}/{key}", self.get, methods=["GET"])

    async def list_by_kind(self, kind: str):
        keys = await self._observations.list(kind=kind)
        return pb_to_dict(GetObservationsResponse(keys=keys))

    async def get(self, kind: str, name: str, key: str):
        _log.debug(s_("Observation requested", kind=kind, name=name, key=key))
        observation = await self._observations.get(ObservationKey(kind=kind, name=name, key=key.replace("|", "/")))
        return pb_to_dict(GetObservationResponse(observation=observation))
