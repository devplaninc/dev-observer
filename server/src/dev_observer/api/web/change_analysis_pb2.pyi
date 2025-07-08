from google.protobuf import timestamp_pb2 as _timestamp_pb2
from dev_observer.api.types import observations_pb2 as _observations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnrollRepositoryRequest(_message.Message):
    __slots__ = ("repo_id",)
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    def __init__(self, repo_id: _Optional[str] = ...) -> None: ...

class EnrollRepositoryResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class UnenrollRepositoryRequest(_message.Message):
    __slots__ = ("repo_id",)
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    def __init__(self, repo_id: _Optional[str] = ...) -> None: ...

class UnenrollRepositoryResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetChangeSummariesRequest(_message.Message):
    __slots__ = ("repo_id", "start_date", "end_date", "status")
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    status: str
    def __init__(self, repo_id: _Optional[str] = ..., start_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ...) -> None: ...

class ChangeSummary(_message.Message):
    __slots__ = ("id", "repo_id", "status", "observation", "error_message", "analyzed_at", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OBSERVATION_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ANALYZED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    repo_id: str
    status: str
    observation: _observations_pb2.Observation
    error_message: str
    analyzed_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., repo_id: _Optional[str] = ..., status: _Optional[str] = ..., observation: _Optional[_Union[_observations_pb2.Observation, _Mapping]] = ..., error_message: _Optional[str] = ..., analyzed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetChangeSummariesResponse(_message.Message):
    __slots__ = ("summaries",)
    SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    summaries: _containers.RepeatedCompositeFieldContainer[ChangeSummary]
    def __init__(self, summaries: _Optional[_Iterable[_Union[ChangeSummary, _Mapping]]] = ...) -> None: ...

class GetRepositoryEnrollmentStatusRequest(_message.Message):
    __slots__ = ("repo_id",)
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    def __init__(self, repo_id: _Optional[str] = ...) -> None: ...

class GetRepositoryEnrollmentStatusResponse(_message.Message):
    __slots__ = ("enrolled", "last_analysis")
    ENROLLED_FIELD_NUMBER: _ClassVar[int]
    LAST_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    enrolled: bool
    last_analysis: _timestamp_pb2.Timestamp
    def __init__(self, enrolled: bool = ..., last_analysis: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
