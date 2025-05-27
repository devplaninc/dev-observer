from fastapi import APIRouter
from starlette.requests import Request

from dev_observer.api.web.config_pb2 import GetGlobalConfigResponse, UpdateGlobalConfigRequest, \
    UpdateGlobalConfigResponse
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import pb_to_json, parse_dict_pb


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
        return pb_to_json(GetGlobalConfigResponse(config=config))

    async def update(self, request: Request):
        config = parse_dict_pb(await request.json(), UpdateGlobalConfigRequest()).config
        updated = await self._store.set_global_config(config)
        return pb_to_json(UpdateGlobalConfigResponse(config=updated))

