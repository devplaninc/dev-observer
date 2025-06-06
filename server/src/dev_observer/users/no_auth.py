from typing import Optional

from dev_observer.users.provider import UsersProvider, Requestish


class NoAuthUsersProvider(UsersProvider):

    def user_management_enabled(self) -> bool:
        return False

    def get_public_api_key(self) -> Optional[str]:
        return None

    def is_request_logged_in(self, req: Requestish) -> bool:
        return True