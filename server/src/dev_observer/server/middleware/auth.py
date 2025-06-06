import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from dev_observer.users.provider import UsersProvider

_log = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    _users: UsersProvider

    def __init__(self, users: UsersProvider):
        self._users = users

    async def verify_token(
            self,
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
            request: Request = None
    ):
        if request.url.path == "/api/v1/config/users/status":
            return
        if not self._users.user_management_enabled():
            return

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not self._users.is_request_logged_in(request):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not authorized",
            )
