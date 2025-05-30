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
