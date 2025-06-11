from github import Auth

from dev_observer.repository.github import GithubAuthProvider


class GithubTokenAuthProvider(GithubAuthProvider):
    _token: str

    def __init__(self, token: str):
        self._token = token

    async def get_auth(self) -> Auth:
        return Auth.Token(self._token)

    async def get_cli_token_prefix(self, url: str, full_name: str) -> str:
        return self._token


