from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChangeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHANGE_TYPE_UNSPECIFIED: _ClassVar[ChangeType]
    CHANGE_TYPE_ADDED: _ClassVar[ChangeType]
    CHANGE_TYPE_MODIFIED: _ClassVar[ChangeType]
    CHANGE_TYPE_DELETED: _ClassVar[ChangeType]
    CHANGE_TYPE_RENAMED: _ClassVar[ChangeType]

class ChangesSummaryStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHANGES_SUMMARY_STATUS_UNSPECIFIED: _ClassVar[ChangesSummaryStatus]
    CHANGES_SUMMARY_STATUS_PENDING: _ClassVar[ChangesSummaryStatus]
    CHANGES_SUMMARY_STATUS_PROCESSING: _ClassVar[ChangesSummaryStatus]
    CHANGES_SUMMARY_STATUS_COMPLETED: _ClassVar[ChangesSummaryStatus]
    CHANGES_SUMMARY_STATUS_FAILED: _ClassVar[ChangesSummaryStatus]
CHANGE_TYPE_UNSPECIFIED: ChangeType
CHANGE_TYPE_ADDED: ChangeType
CHANGE_TYPE_MODIFIED: ChangeType
CHANGE_TYPE_DELETED: ChangeType
CHANGE_TYPE_RENAMED: ChangeType
CHANGES_SUMMARY_STATUS_UNSPECIFIED: ChangesSummaryStatus
CHANGES_SUMMARY_STATUS_PENDING: ChangesSummaryStatus
CHANGES_SUMMARY_STATUS_PROCESSING: ChangesSummaryStatus
CHANGES_SUMMARY_STATUS_COMPLETED: ChangesSummaryStatus
CHANGES_SUMMARY_STATUS_FAILED: ChangesSummaryStatus

class GitHubChangesSummary(_message.Message):
    __slots__ = ("id", "repo_id", "repo_full_name", "created_at", "analysis_period_start", "analysis_period_end", "content", "status", "error_message")
    ID_FIELD_NUMBER: _ClassVar[int]
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    REPO_FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_PERIOD_START_FIELD_NUMBER: _ClassVar[int]
    ANALYSIS_PERIOD_END_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    id: str
    repo_id: str
    repo_full_name: str
    created_at: _timestamp_pb2.Timestamp
    analysis_period_start: _timestamp_pb2.Timestamp
    analysis_period_end: _timestamp_pb2.Timestamp
    content: ChangesSummaryContent
    status: ChangesSummaryStatus
    error_message: str
    def __init__(self, id: _Optional[str] = ..., repo_id: _Optional[str] = ..., repo_full_name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., analysis_period_start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., analysis_period_end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., content: _Optional[_Union[ChangesSummaryContent, _Mapping]] = ..., status: _Optional[_Union[ChangesSummaryStatus, str]] = ..., error_message: _Optional[str] = ...) -> None: ...

class ChangesSummaryContent(_message.Message):
    __slots__ = ("summary", "commits", "file_changes", "pull_requests", "issues", "statistics")
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    COMMITS_FIELD_NUMBER: _ClassVar[int]
    FILE_CHANGES_FIELD_NUMBER: _ClassVar[int]
    PULL_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ISSUES_FIELD_NUMBER: _ClassVar[int]
    STATISTICS_FIELD_NUMBER: _ClassVar[int]
    summary: str
    commits: _containers.RepeatedCompositeFieldContainer[CommitInfo]
    file_changes: _containers.RepeatedCompositeFieldContainer[FileChange]
    pull_requests: _containers.RepeatedCompositeFieldContainer[PullRequestInfo]
    issues: _containers.RepeatedCompositeFieldContainer[IssueInfo]
    statistics: ChangesStatistics
    def __init__(self, summary: _Optional[str] = ..., commits: _Optional[_Iterable[_Union[CommitInfo, _Mapping]]] = ..., file_changes: _Optional[_Iterable[_Union[FileChange, _Mapping]]] = ..., pull_requests: _Optional[_Iterable[_Union[PullRequestInfo, _Mapping]]] = ..., issues: _Optional[_Iterable[_Union[IssueInfo, _Mapping]]] = ..., statistics: _Optional[_Union[ChangesStatistics, _Mapping]] = ...) -> None: ...

class CommitInfo(_message.Message):
    __slots__ = ("sha", "message", "author", "committed_at", "files_changed", "additions", "deletions")
    SHA_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    COMMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    FILES_CHANGED_FIELD_NUMBER: _ClassVar[int]
    ADDITIONS_FIELD_NUMBER: _ClassVar[int]
    DELETIONS_FIELD_NUMBER: _ClassVar[int]
    sha: str
    message: str
    author: str
    committed_at: _timestamp_pb2.Timestamp
    files_changed: _containers.RepeatedScalarFieldContainer[str]
    additions: int
    deletions: int
    def __init__(self, sha: _Optional[str] = ..., message: _Optional[str] = ..., author: _Optional[str] = ..., committed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., files_changed: _Optional[_Iterable[str]] = ..., additions: _Optional[int] = ..., deletions: _Optional[int] = ...) -> None: ...

class FileChange(_message.Message):
    __slots__ = ("file_path", "change_type", "additions", "deletions", "language")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    CHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ADDITIONS_FIELD_NUMBER: _ClassVar[int]
    DELETIONS_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    change_type: ChangeType
    additions: int
    deletions: int
    language: str
    def __init__(self, file_path: _Optional[str] = ..., change_type: _Optional[_Union[ChangeType, str]] = ..., additions: _Optional[int] = ..., deletions: _Optional[int] = ..., language: _Optional[str] = ...) -> None: ...

class PullRequestInfo(_message.Message):
    __slots__ = ("number", "title", "state", "author", "created_at", "updated_at", "merged_at", "labels", "additions", "deletions")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    MERGED_AT_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    ADDITIONS_FIELD_NUMBER: _ClassVar[int]
    DELETIONS_FIELD_NUMBER: _ClassVar[int]
    number: int
    title: str
    state: str
    author: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    merged_at: _timestamp_pb2.Timestamp
    labels: _containers.RepeatedScalarFieldContainer[str]
    additions: int
    deletions: int
    def __init__(self, number: _Optional[int] = ..., title: _Optional[str] = ..., state: _Optional[str] = ..., author: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., merged_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., labels: _Optional[_Iterable[str]] = ..., additions: _Optional[int] = ..., deletions: _Optional[int] = ...) -> None: ...

class IssueInfo(_message.Message):
    __slots__ = ("number", "title", "state", "author", "created_at", "updated_at", "closed_at", "labels")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CLOSED_AT_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    number: int
    title: str
    state: str
    author: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    closed_at: _timestamp_pb2.Timestamp
    labels: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, number: _Optional[int] = ..., title: _Optional[str] = ..., state: _Optional[str] = ..., author: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., closed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., labels: _Optional[_Iterable[str]] = ...) -> None: ...

class ChangesStatistics(_message.Message):
    __slots__ = ("total_commits", "total_additions", "total_deletions", "total_files_changed", "total_pull_requests", "total_issues", "language_stats")
    TOTAL_COMMITS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ADDITIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DELETIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FILES_CHANGED_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PULL_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ISSUES_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_STATS_FIELD_NUMBER: _ClassVar[int]
    total_commits: int
    total_additions: int
    total_deletions: int
    total_files_changed: int
    total_pull_requests: int
    total_issues: int
    language_stats: _containers.RepeatedCompositeFieldContainer[LanguageStats]
    def __init__(self, total_commits: _Optional[int] = ..., total_additions: _Optional[int] = ..., total_deletions: _Optional[int] = ..., total_files_changed: _Optional[int] = ..., total_pull_requests: _Optional[int] = ..., total_issues: _Optional[int] = ..., language_stats: _Optional[_Iterable[_Union[LanguageStats, _Mapping]]] = ...) -> None: ...

class LanguageStats(_message.Message):
    __slots__ = ("language", "files_changed", "additions", "deletions")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    FILES_CHANGED_FIELD_NUMBER: _ClassVar[int]
    ADDITIONS_FIELD_NUMBER: _ClassVar[int]
    DELETIONS_FIELD_NUMBER: _ClassVar[int]
    language: str
    files_changed: int
    additions: int
    deletions: int
    def __init__(self, language: _Optional[str] = ..., files_changed: _Optional[int] = ..., additions: _Optional[int] = ..., deletions: _Optional[int] = ...) -> None: ...
