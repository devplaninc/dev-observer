from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessingItem(_message.Message):
    __slots__ = ("id", "next_processing", "last_processed", "last_error", "no_processing", "github_repo_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NEXT_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    LAST_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    LAST_ERROR_FIELD_NUMBER: _ClassVar[int]
    NO_PROCESSING_FIELD_NUMBER: _ClassVar[int]
    GITHUB_REPO_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    next_processing: _timestamp_pb2.Timestamp
    last_processed: _timestamp_pb2.Timestamp
    last_error: str
    no_processing: bool
    github_repo_id: str
    def __init__(self, id: _Optional[str] = ..., next_processing: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_processed: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_error: _Optional[str] = ..., no_processing: bool = ..., github_repo_id: _Optional[str] = ...) -> None: ...
