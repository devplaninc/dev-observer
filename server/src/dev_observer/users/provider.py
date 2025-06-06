from abc import abstractmethod
from typing import Protocol, Optional, Mapping


class Requestish(Protocol):
    @property
    def headers(self) -> Mapping[str, str]:
        ...


class UsersProvider(Protocol):

    @abstractmethod
    def user_management_enabled(self) -> bool:
        ...

    @abstractmethod
    def get_public_api_key(self) -> Optional[str]:
        ...

    @abstractmethod
    def is_request_logged_in(self, req: Requestish) -> bool:
        ...
