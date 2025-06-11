import logging
import subprocess
from abc import abstractmethod
from typing import Protocol

from github import Auth
from github import Github

from dev_observer.repository.parser import parse_github_url
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo

_log = logging.getLogger(__name__)


class GithubAuthProvider(Protocol):
    @abstractmethod
    async def get_auth(self, url: str, full_name: str) -> Auth:
        ...

    @abstractmethod
    async def get_cli_token_prefix(self, url: str, full_name: str) -> str:
        ...


class GithubProvider(GitRepositoryProvider):
    _auth_provider: GithubAuthProvider

    def __init__(self, auth_provider: GithubAuthProvider):
        self._auth_provider = auth_provider

    async def get_repo(self, url: str) -> RepositoryInfo:
        parsed = parse_github_url(url)
        full_name = f"{parsed.owner}/{parsed.name}"
        auth = await self._auth_provider.get_auth(url, full_name)
        with Github(auth=auth) as gh:
            repo = gh.get_repo(full_name)

        return RepositoryInfo(
            owner=parsed.owner,
            name=parsed.name,
            clone_url=repo.clone_url,
            size_kb=repo.size,
        )

    async def clone(self, repo: RepositoryInfo, dest: str):
        full_name = f"{repo.owner}/{repo.name}"
        token = await self._auth_provider.get_cli_token_prefix(repo.clone_url, full_name)
        clone_url = repo.clone_url.replace("https://", f"https://{token}@")
        result = subprocess.run(
            ["git", "clone", "--depth=1", clone_url, dest],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to clone repository: {result.stderr}")
