import logging

from fastapi import APIRouter
from starlette.requests import Request

from dev_observer.api.types.processing_pb2 import ProcessingItemKey
from dev_observer.api.types.sites_pb2 import WebSite
from dev_observer.api.web.sites_pb2 import AddWebSiteRequest, AddWebSiteResponse, \
    ListWebSitesResponse, GetWebSiteResponse, DeleteWebSiteResponse, RescanWebSiteResponse
from dev_observer.log import s_
from dev_observer.storage.provider import StorageProvider
from dev_observer.util import parse_dict_pb, Clock, RealClock, pb_to_dict

_log = logging.getLogger(__name__)


class WebSitesService:
    _store: StorageProvider
    _clock: Clock

    router: APIRouter

    def __init__(self, store: StorageProvider, clock: Clock = RealClock()):
        self._store = store
        self._clock = clock
        self.router = APIRouter()

        self.router.add_api_route("/websites", self.add, methods=["POST"])
        self.router.add_api_route("/websites", self.list, methods=["GET"])
        self.router.add_api_route("/websites/{site_id}", self.get, methods=["GET"])
        self.router.add_api_route("/websites/{site_id}", self.delete, methods=["DELETE"])
        self.router.add_api_route("/websites/{site_id}/rescan", self.rescan, methods=["POST"])

    async def add(self, req: Request):
        request = parse_dict_pb(await req.json(), AddWebSiteRequest())
        _log.debug(s_("Adding website", request=request))
        site = await self._store.add_web_site(WebSite(url=request.url))
        return pb_to_dict(AddWebSiteResponse(site=site))

    async def get(self, site_id: str):
        site = await self._store.get_web_site(site_id)
        return pb_to_dict(GetWebSiteResponse(site=site))

    async def delete(self, site_id: str):
        await self._store.delete_web_site(site_id)
        sites = await self._store.get_web_sites()
        return pb_to_dict(DeleteWebSiteResponse(sites=sites))

    async def list(self):
        sites = await self._store.get_web_sites()
        return pb_to_dict(ListWebSitesResponse(sites=sites))

    async def rescan(self, site_id: str):
        site = await self._store.get_web_site(site_id)
        await self._store.set_next_processing_time(
            ProcessingItemKey(website_url=site.url), self._clock.now(),
        )
        return pb_to_dict(RescanWebSiteResponse())
