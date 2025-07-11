from dev_observer.api.types import repo_pb2 as _repo_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListGithubRepositoriesResponse(_message.Message):
    __slots__ = ("repos",)
    REPOS_FIELD_NUMBER: _ClassVar[int]
    repos: _containers.RepeatedCompositeFieldContainer[_repo_pb2.GitHubRepository]
    def __init__(self, repos: _Optional[_Iterable[_Union[_repo_pb2.GitHubRepository, _Mapping]]] = ...) -> None: ...

class AddGithubRepositoryRequest(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class AddGithubRepositoryResponse(_message.Message):
    __slots__ = ("repo",)
    REPO_FIELD_NUMBER: _ClassVar[int]
    repo: _repo_pb2.GitHubRepository
    def __init__(self, repo: _Optional[_Union[_repo_pb2.GitHubRepository, _Mapping]] = ...) -> None: ...

class RescanRepositoryResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetRepositoryResponse(_message.Message):
    __slots__ = ("repo",)
    REPO_FIELD_NUMBER: _ClassVar[int]
    repo: _repo_pb2.GitHubRepository
    def __init__(self, repo: _Optional[_Union[_repo_pb2.GitHubRepository, _Mapping]] = ...) -> None: ...

class DeleteRepositoryResponse(_message.Message):
    __slots__ = ("repos",)
    REPOS_FIELD_NUMBER: _ClassVar[int]
    repos: _containers.RepeatedCompositeFieldContainer[_repo_pb2.GitHubRepository]
    def __init__(self, repos: _Optional[_Iterable[_Union[_repo_pb2.GitHubRepository, _Mapping]]] = ...) -> None: ...

class EnrollRepositoryForChangeAnalysisRequest(_message.Message):
    __slots__ = ("repo_id",)
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    def __init__(self, repo_id: _Optional[str] = ...) -> None: ...

class EnrollRepositoryForChangeAnalysisResponse(_message.Message):
    __slots__ = ("repo",)
    REPO_FIELD_NUMBER: _ClassVar[int]
    repo: _repo_pb2.GitHubRepository
    def __init__(self, repo: _Optional[_Union[_repo_pb2.GitHubRepository, _Mapping]] = ...) -> None: ...

class UnenrollRepositoryFromChangeAnalysisRequest(_message.Message):
    __slots__ = ("repo_id",)
    REPO_ID_FIELD_NUMBER: _ClassVar[int]
    repo_id: str
    def __init__(self, repo_id: _Optional[str] = ...) -> None: ...

class UnenrollRepositoryFromChangeAnalysisResponse(_message.Message):
    __slots__ = ("repo",)
    REPO_FIELD_NUMBER: _ClassVar[int]
    repo: _repo_pb2.GitHubRepository
    def __init__(self, repo: _Optional[_Union[_repo_pb2.GitHubRepository, _Mapping]] = ...) -> None: ...

class GetChangeAnalysesRequest(_message.Message):
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

class GetChangeAnalysesResponse(_message.Message):
    __slots__ = ("analyses",)
    ANALYSES_FIELD_NUMBER: _ClassVar[int]
    analyses: _containers.RepeatedCompositeFieldContainer[_repo_pb2.RepoChangeAnalysis]
    def __init__(self, analyses: _Optional[_Iterable[_Union[_repo_pb2.RepoChangeAnalysis, _Mapping]]] = ...) -> None: ...

class GetChangeAnalysisRequest(_message.Message):
    __slots__ = ("analysis_id",)
    ANALYSIS_ID_FIELD_NUMBER: _ClassVar[int]
    analysis_id: str
    def __init__(self, analysis_id: _Optional[str] = ...) -> None: ...

class GetChangeAnalysisResponse(_message.Message):
    __slots__ = ("analysis",)
    ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    analysis: _repo_pb2.RepoChangeAnalysis
    def __init__(self, analysis: _Optional[_Union[_repo_pb2.RepoChangeAnalysis, _Mapping]] = ...) -> None: ...
