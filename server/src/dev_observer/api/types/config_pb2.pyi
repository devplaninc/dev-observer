from dev_observer.api.types import observations_pb2 as _observations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GlobalConfig(_message.Message):
    __slots__ = ("analysis", "repo_analysis")
    ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    REPO_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    analysis: AnalysisConfig
    repo_analysis: RepoAnalysisConfig
    def __init__(self, analysis: _Optional[_Union[AnalysisConfig, _Mapping]] = ..., repo_analysis: _Optional[_Union[RepoAnalysisConfig, _Mapping]] = ...) -> None: ...

class AnalysisConfig(_message.Message):
    __slots__ = ("repo_analyzers", "site_analyzers", "disable_masking")
    REPO_ANALYZERS_FIELD_NUMBER: _ClassVar[int]
    SITE_ANALYZERS_FIELD_NUMBER: _ClassVar[int]
    DISABLE_MASKING_FIELD_NUMBER: _ClassVar[int]
    repo_analyzers: _containers.RepeatedCompositeFieldContainer[_observations_pb2.Analyzer]
    site_analyzers: _containers.RepeatedCompositeFieldContainer[_observations_pb2.Analyzer]
    disable_masking: bool
    def __init__(self, repo_analyzers: _Optional[_Iterable[_Union[_observations_pb2.Analyzer, _Mapping]]] = ..., site_analyzers: _Optional[_Iterable[_Union[_observations_pb2.Analyzer, _Mapping]]] = ..., disable_masking: bool = ...) -> None: ...

class UserManagementStatus(_message.Message):
    __slots__ = ("enabled", "public_api_key")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_API_KEY_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    public_api_key: str
    def __init__(self, enabled: bool = ..., public_api_key: _Optional[str] = ...) -> None: ...

class RepoAnalysisConfig(_message.Message):
    __slots__ = ("flatten", "processing_interval_sec", "disabled")
    class Flatten(_message.Message):
        __slots__ = ("compress", "remove_empty_lines", "out_style", "max_tokens_per_chunk", "max_repo_size_mb", "ignore_pattern", "large_repo_threshold_mb", "large_repo_ignore_pattern", "compress_large")
        COMPRESS_FIELD_NUMBER: _ClassVar[int]
        REMOVE_EMPTY_LINES_FIELD_NUMBER: _ClassVar[int]
        OUT_STYLE_FIELD_NUMBER: _ClassVar[int]
        MAX_TOKENS_PER_CHUNK_FIELD_NUMBER: _ClassVar[int]
        MAX_REPO_SIZE_MB_FIELD_NUMBER: _ClassVar[int]
        IGNORE_PATTERN_FIELD_NUMBER: _ClassVar[int]
        LARGE_REPO_THRESHOLD_MB_FIELD_NUMBER: _ClassVar[int]
        LARGE_REPO_IGNORE_PATTERN_FIELD_NUMBER: _ClassVar[int]
        COMPRESS_LARGE_FIELD_NUMBER: _ClassVar[int]
        compress: bool
        remove_empty_lines: bool
        out_style: str
        max_tokens_per_chunk: int
        max_repo_size_mb: int
        ignore_pattern: str
        large_repo_threshold_mb: int
        large_repo_ignore_pattern: str
        compress_large: bool
        def __init__(self, compress: bool = ..., remove_empty_lines: bool = ..., out_style: _Optional[str] = ..., max_tokens_per_chunk: _Optional[int] = ..., max_repo_size_mb: _Optional[int] = ..., ignore_pattern: _Optional[str] = ..., large_repo_threshold_mb: _Optional[int] = ..., large_repo_ignore_pattern: _Optional[str] = ..., compress_large: bool = ...) -> None: ...
    FLATTEN_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_INTERVAL_SEC_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    flatten: RepoAnalysisConfig.Flatten
    processing_interval_sec: int
    disabled: bool
    def __init__(self, flatten: _Optional[_Union[RepoAnalysisConfig.Flatten, _Mapping]] = ..., processing_interval_sec: _Optional[int] = ..., disabled: bool = ...) -> None: ...
