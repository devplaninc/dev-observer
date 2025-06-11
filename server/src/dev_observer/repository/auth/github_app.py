import logging

from github import Auth, GithubIntegration

from dev_observer.repository.github import GithubAuthProvider
from dev_observer.storage.provider import StorageProvider

_log = logging.getLogger(__name__)


class GithubAppAuthProvider(GithubAuthProvider):
    _private_key: str
    _app_id: str

    def __init__(self, app_id: str, private_key: str):
        self._private_key = private_key
        self._app_id = app_id

    async def get_auth(self, url: str, full_name: str) -> Auth:
        parts = full_name.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repository name [{full_name}]")
        auth = Auth.AppAuth(self._app_id, self._private_key)
        with GithubIntegration(auth=auth) as gh:
            installation = gh.get_repo_installation(parts[0], parts[1])
            return auth.get_installation_auth(installation.id)

    async def get_cli_token_prefix(self, url: str, full_name: str) -> str:
        parts = full_name.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repository name [{full_name}]")
        auth = Auth.AppAuth(self._app_id, self._private_key)
        with GithubIntegration(auth=auth) as gh:
            installation = gh.get_repo_installation(parts[0], parts[1])
            token = gh.get_access_token(installation.id).token
            return f"x-access-token:{token}"




