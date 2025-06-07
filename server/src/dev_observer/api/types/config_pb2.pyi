from dev_observer.api.types import observations_pb2 as _observations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GlobalConfig(_message.Message):
    __slots__ = ("analysis",)
    ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    analysis: AnalysisConfig
    def __init__(self, analysis: _Optional[_Union[AnalysisConfig, _Mapping]] = ...) -> None: ...

class AnalysisConfig(_message.Message):
    __slots__ = ("repo_analyzers", "site_analyzers")
    REPO_ANALYZERS_FIELD_NUMBER: _ClassVar[int]
    SITE_ANALYZERS_FIELD_NUMBER: _ClassVar[int]
    repo_analyzers: _containers.RepeatedCompositeFieldContainer[_observations_pb2.Analyzer]
    site_analyzers: _containers.RepeatedCompositeFieldContainer[_observations_pb2.Analyzer]
    def __init__(self, repo_analyzers: _Optional[_Iterable[_Union[_observations_pb2.Analyzer, _Mapping]]] = ..., site_analyzers: _Optional[_Iterable[_Union[_observations_pb2.Analyzer, _Mapping]]] = ...) -> None: ...

class UserManagementStatus(_message.Message):
    __slots__ = ("enabled", "public_api_key")
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_API_KEY_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    public_api_key: str
    def __init__(self, enabled: bool = ..., public_api_key: _Optional[str] = ...) -> None: ...
