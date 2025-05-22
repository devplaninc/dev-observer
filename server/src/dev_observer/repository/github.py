import logging

from github import Auth
from github import Github

from dev_observer.repository.parser import parse_github_url
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo

_log = logging.getLogger(__name__)


class GithubProvider(GitRepositoryProvider):
    _gh: Github
    _auth: Auth

    def __init__(self, auth: Auth):
        self._auth = auth
        self._gh = Github(auth=auth)

    def get_repo(self, url: str) -> RepositoryInfo:
        parsed = parse_github_url(url)
        full_name = f"{parsed.owner}/{parsed.name}"
        repo = self._gh.get_repo(full_name)

        return RepositoryInfo(
            owner=parsed.owner,
            name=parsed.name,
            clone_url=repo.clone_url,
            size_kb=repo.size,
        )

    def get_private_clone_url(self, repo: RepositoryInfo) -> str:
        token = self._auth.token
        return repo.clone_url.replace("https://", f"https://{token}@")
