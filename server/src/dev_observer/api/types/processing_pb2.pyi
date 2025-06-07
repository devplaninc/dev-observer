from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessingItemKey(_message.Message):
    __slots__ = ("github_repo_id", "website_url")
    GITHUB_REPO_ID_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_URL_FIELD_NUMBER: _ClassVar[int]
    github_repo_id: str
    website_url: str
    def __init__(self, github_repo_id: _Optional[str] = ..., website_url: _Optional[str] = ...) -> None: ...

class ProcessingItem(_message.Message):
    __slots__ = ("key", "next_processing", "last_processed", "last_error", "no_processing")
    KEY_FIELD_NUMBER: _ClassVar[int]
    NEXT_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    LAST_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    LAST_ERROR_FIELD_NUMBER: _ClassVar[int]
    NO_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    key: ProcessingItemKey
    next_processing: _timestamp_pb2.Timestamp
    last_processed: _timestamp_pb2.Timestamp
    last_error: str
    no_processing: bool
    def __init__(self, key: _Optional[_Union[ProcessingItemKey, _Mapping]] = ..., next_processing: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_processed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_error: _Optional[str] = ..., no_processing: bool = ...) -> None: ...
