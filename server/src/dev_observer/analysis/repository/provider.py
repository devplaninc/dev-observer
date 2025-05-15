import dataclasses


@dataclasses.dataclass
class RepositoryInfo:
    owner: str
    name: str
    clone_url: str
    size_kb: int


class GitRepositoryProvider:
    def get_repo(self, url: str) -> RepositoryInfo:
        ...

    def get_private_clone_url(self, repo: RepositoryInfo) -> str:
        ...
