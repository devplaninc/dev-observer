from dev_observer.api.types import changes_pb2 as _changes_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListChangesSummariesRequest(_message.Message):
    __slots__ = ("repo_id", "limit", "offset")
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    limit: int
    offset: int
    def __init__(self, repo_id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ListChangesSummariesResponse(_message.Message):
    __slots__ = ("summaries", "total_count")
    SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    summaries: _containers.RepeatedCompositeFieldContainer[_changes_pb2.GitHubChangesSummary]
    total_count: int
    def __init__(self, summaries: _Optional[_Iterable[_Union[_changes_pb2.GitHubChangesSummary, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetChangesSummaryRequest(_message.Message):
    __slots__ = ("summary_id",)
    SUMMARY_ID_FIELD_NUMBER: _ClassVar[int]
    summary_id: str
    def __init__(self, summary_id: _Optional[str] = ...) -> None: ...

class GetChangesSummaryResponse(_message.Message):
    __slots__ = ("summary",)
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    summary: _changes_pb2.GitHubChangesSummary
    def __init__(self, summary: _Optional[_Union[_changes_pb2.GitHubChangesSummary, _Mapping]] = ...) -> None: ...

class CreateChangesSummaryRequest(_message.Message):
    __slots__ = ("repo_id", "days_back")
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    DAYS_BACK_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    days_back: int
    def __init__(self, repo_id: _Optional[str] = ..., days_back: _Optional[int] = ...) -> None: ...

class CreateChangesSummaryResponse(_message.Message):
    __slots__ = ("summary",)
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    summary: _changes_pb2.GitHubChangesSummary
    def __init__(self, summary: _Optional[_Union[_changes_pb2.GitHubChangesSummary, _Mapping]] = ...) -> None: ...

class DeleteChangesSummaryRequest(_message.Message):
    __slots__ = ("summary_id",)
    SUMMARY_ID_FIELD_NUMBER: _ClassVar[int]
    summary_id: str
    def __init__(self, summary_id: _Optional[str] = ...) -> None: ...

class DeleteChangesSummaryResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
