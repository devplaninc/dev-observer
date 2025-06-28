from dev_observer.api.types import sites_pb2 as _sites_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListWebSitesResponse(_message.Message):
    __slots__ = ("sites",)
    SITES_FIELD_NUMBER: _ClassVar[int]
    sites: _containers.RepeatedCompositeFieldContainer[_sites_pb2.WebSite]
    def __init__(self, sites: _Optional[_Iterable[_Union[_sites_pb2.WebSite, _Mapping]]] = ...) -> None: ...

class AddWebSiteRequest(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class AddWebSiteResponse(_message.Message):
    __slots__ = ("site",)
    SITE_FIELD_NUMBER: _ClassVar[int]
    site: _sites_pb2.WebSite
    def __init__(self, site: _Optional[_Union[_sites_pb2.WebSite, _Mapping]] = ...) -> None: ...

class RescanWebSiteResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetWebSiteResponse(_message.Message):
    __slots__ = ("site",)
    SITE_FIELD_NUMBER: _ClassVar[int]
    site: _sites_pb2.WebSite
    def __init__(self, site: _Optional[_Union[_sites_pb2.WebSite, _Mapping]] = ...) -> None: ...

class DeleteWebSiteResponse(_message.Message):
    __slots__ = ("sites",)
    SITES_FIELD_NUMBER: _ClassVar[int]
    sites: _containers.RepeatedCompositeFieldContainer[_sites_pb2.WebSite]
    def __init__(self, sites: _Optional[_Iterable[_Union[_sites_pb2.WebSite, _Mapping]]] = ...) -> None: ...
