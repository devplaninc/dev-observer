import os
from typing import Optional

from github import Auth
from github import Github

from dev_observer.analysis.repository.parser import parse_github_url
from dev_observer.analysis.repository.provider import GitRepositoryProvider, RepositoryInfo


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


def github_provider_from_env() -> Optional[GithubProvider]:
    auth = github_auth_from_env()
    if auth is None:
        return None
    return GithubProvider(auth)


def github_auth_from_env() -> Optional[Auth]:
    auth_type = os.environ.get("GITHUB_AUTH_TYPE", None)
    print(f"auth_type: {auth_type}")
    if auth_type is None:
        return None
    match auth_type:
        case "token":
            return Auth.Token(os.environ["GITHUB_PERSONAL_TOKEN"])
    raise ValueError(f"Unsupported auth type: {auth_type}")
