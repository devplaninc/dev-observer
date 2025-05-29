import logging

from fastapi import APIRouter
from starlette.requests import Request

from dev_observer.api.web.config_pb2 import GetGlobalConfigResponse, UpdateGlobalConfigRequest, \
    UpdateGlobalConfigResponse
from dev_observer.log import s_
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import parse_dict_pb, pb_to_dict

_log = logging.getLogger(__name__)

class ConfigService:
    _store: StorageProvider

    router: APIRouter

    def __init__(self, store: StorageProvider):
        self._store = store
        self.router = APIRouter()

        self.router.add_api_route("/config", self.get, methods=["GET"])
        self.router.add_api_route("/config", self.update, methods=["POST"])

    async def get(self):
        config = await self._store.get_global_config()
        return pb_to_dict(GetGlobalConfigResponse(config=config))

    async def update(self, request: Request):
        config = parse_dict_pb(await request.json(), UpdateGlobalConfigRequest()).config
        _log.debug(s_("Updating config", config=config))
        updated = await self._store.set_global_config(config)
        return pb_to_dict(UpdateGlobalConfigResponse(config=updated))

