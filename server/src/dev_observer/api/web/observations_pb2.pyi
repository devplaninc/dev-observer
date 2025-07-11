from dev_observer.api.types import observations_pb2 as _observations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetObservationsResponse(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[_observations_pb2.ObservationKey]
    def __init__(self, keys: _Optional[_Iterable[_Union[_observations_pb2.ObservationKey, _Mapping]]] = ...) -> None: ...

class GetObservationResponse(_message.Message):
    __slots__ = ("observation",)
    OBSERVATION_FIELD_NUMBER: _ClassVar[int]
    observation: _observations_pb2.Observation
    def __init__(self, observation: _Optional[_Union[_observations_pb2.Observation, _Mapping]] = ...) -> None: ...

class GetChangeSummariesRequest(_message.Message):
    __slots__ = ("repo_id", "date_from", "date_to", "status")
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FROM_FIELD_NUMBER: _ClassVar[int]
    DATE_TO_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    date_from: str
    date_to: str
    status: str
    def __init__(self, repo_id: _Optional[str] = ..., date_from: _Optional[str] = ..., date_to: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...

class GetChangeSummariesResponse(_message.Message):
    __slots__ = ("summaries",)
    SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    summaries: _containers.RepeatedCompositeFieldContainer[ChangeSummary]
    def __init__(self, summaries: _Optional[_Iterable[_Union[ChangeSummary, _Mapping]]] = ...) -> None: ...

class ChangeSummary(_message.Message):
    __slots__ = ("job_id", "repo_id", "repo_name", "status", "observation_key", "error_message", "analyzed_at", "summary_content")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    REPO_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    OBSERVATION_KEY_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ANALYZED_AT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_CONTENT_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    repo_id: str
    repo_name: str
    status: str
    observation_key: str
    error_message: str
    analyzed_at: str
    summary_content: str
    def __init__(self, job_id: _Optional[str] = ..., repo_id: _Optional[str] = ..., repo_name: _Optional[str] = ..., status: _Optional[str] = ..., observation_key: _Optional[str] = ..., error_message: _Optional[str] = ..., analyzed_at: _Optional[str] = ..., summary_content: _Optional[str] = ...) -> None: ...
