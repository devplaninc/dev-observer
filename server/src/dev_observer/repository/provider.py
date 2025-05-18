import dataclasses
from abc import abstractmethod
from typing import Protocol


@dataclasses.dataclass
class RepositoryInfo:
    owner: str
    name: str
    clone_url: str
    size_kb: int


class GitRepositoryProvider(Protocol):
    @abstractmethod
    def get_repo(self, url: str) -> RepositoryInfo:
        ...

    @abstractmethod
    def get_private_clone_url(self, repo: RepositoryInfo) -> str:
        ...
