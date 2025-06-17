from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GitHubRepository(_message.Message):
    __slots__ = ("id", "name", "full_name", "url", "description", "properties")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    full_name: str
    url: str
    description: str
    properties: GitProperties
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., full_name: _Optional[str] = ..., url: _Optional[str] = ..., description: _Optional[str] = ..., properties: _Optional[_Union[GitProperties, _Mapping]] = ...) -> None: ...

class GitProperties(_message.Message):
    __slots__ = ("app_info", "meta")
    APP_INFO_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    app_info: GitAppInfo
    meta: GitMeta
    def __init__(self, app_info: _Optional[_Union[GitAppInfo, _Mapping]] = ..., meta: _Optional[_Union[GitMeta, _Mapping]] = ...) -> None: ...

class GitMeta(_message.Message):
    __slots__ = ("last_refresh", "clone_url", "size_kb")
    LAST_REFRESH_FIELD_NUMBER: _ClassVar[int]
    CLONE_URL_FIELD_NUMBER: _ClassVar[int]
    SIZE_KB_FIELD_NUMBER: _ClassVar[int]
    last_refresh: _timestamp_pb2.Timestamp
    clone_url: str
    size_kb: int
    def __init__(self, last_refresh: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., clone_url: _Optional[str] = ..., size_kb: _Optional[int] = ...) -> None: ...

class GitAppInfo(_message.Message):
    __slots__ = ("last_refresh", "installation_id")
    LAST_REFRESH_FIELD_NUMBER: _ClassVar[int]
    INSTALLATION_ID_FIELD_NUMBER: _ClassVar[int]
    last_refresh: _timestamp_pb2.Timestamp
    installation_id: int
    def __init__(self, last_refresh: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., installation_id: _Optional[int] = ...) -> None: ...
