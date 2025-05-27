from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ObservationKey(_message.Message):
    __slots__ = ("kind", "name", "key")
    KIND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    kind: str
    name: str
    key: str
    def __init__(self, kind: _Optional[str] = ..., name: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class Observation(_message.Message):
    __slots__ = ("key", "content")
    KEY_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    key: ObservationKey
    content: bytes
    def __init__(self, key: _Optional[_Union[ObservationKey, _Mapping]] = ..., content: _Optional[bytes] = ...) -> None: ...
