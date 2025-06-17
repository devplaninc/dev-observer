import dataclasses

from dev_observer.api.types.repo_pb2 import GitHubRepository


@dataclasses.dataclass
class ObservedRepo:
    url: str
    github_repo: GitHubRepository
