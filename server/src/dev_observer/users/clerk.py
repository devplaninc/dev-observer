from typing import Optional

from clerk_backend_api import Clerk, AuthenticateRequestOptions

from dev_observer.users.provider import UsersProvider, Requestish


class ClerkUsersProvider(UsersProvider):
    _clerk: Clerk
    _public_key: str

    def __init__(self, private_key: str, public_key: str):
        self._clerk = Clerk(bearer_auth=private_key)
        self._public_key = public_key

    def user_management_enabled(self) -> bool:
        return True

    def get_public_api_key(self) -> Optional[str]:
        return self._public_key

    def is_request_logged_in(self, req: Requestish) -> bool:
        req_state = self._clerk.authenticate_request(
            req,
            AuthenticateRequestOptions()
        )

        return req_state.is_signed_in
