import logging
from typing import Optional

from github import Auth
from github import Github

from dev_observer.repository.parser import parse_github_url
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo
from dev_observer.log import s_
from dev_observer.settings import settings

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


def detect_github_provider() -> Optional[GithubProvider]:
    auth = detect_github_auth()
    if auth is None:
        return None
    return GithubProvider(auth)


def detect_github_auth() -> Optional[Auth]:
    gh = settings.github
    if gh is None:
        return None
    _log.debug(s_("Detected github auth type.", auth_type=gh.auth_type))
    match gh.auth_type:
        case "token":
            return Auth.Token(gh.personal_token)
    raise ValueError(f"Unsupported auth type: {gh.auth_type}")
