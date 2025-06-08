import pytest
import anyio
from unittest.mock import MagicMock

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials

from dev_observer.server.middleware.auth import AuthMiddleware
from dev_observer.users.provider import UsersProvider


@pytest.fixture
def mock_users_provider():
    provider = MagicMock(spec=UsersProvider)
    return provider


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.url.path = "/api/v1/some/endpoint"
    return request


@pytest.fixture
def auth_middleware_with_api_key(mock_users_provider):
    api_key = "test_api_key"
    return AuthMiddleware(mock_users_provider, [api_key]), api_key


@pytest.fixture
def auth_middleware(mock_users_provider):
    return AuthMiddleware(mock_users_provider, [])


def test_verify_token_with_api_key(auth_middleware_with_api_key, mock_request):
    # Setup
    auth_middleware, api_key = auth_middleware_with_api_key
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=api_key)

    # Execute
    # Use anyio.run to run the async function
    result = anyio.run(lambda: auth_middleware.verify_token(credentials, mock_request))

    # Verify
    # No exception should be raised and the function should return None
    assert result is None
    # The users provider should not be called to check if the request is logged in
    auth_middleware._users.is_request_logged_in.assert_not_called()


def test_verify_token_with_invalid_api_key(auth_middleware_with_api_key, mock_request):
    # Setup
    auth_middleware, _ = auth_middleware_with_api_key
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_key")
    auth_middleware._users.user_management_enabled.return_value = True
    auth_middleware._users.is_request_logged_in.return_value = False

    # Execute and verify
    with pytest.raises(HTTPException) as excinfo:
        anyio.run(lambda: auth_middleware.verify_token(credentials, mock_request))

    # Verify
    assert excinfo.value.status_code == 403
    auth_middleware._users.is_request_logged_in.assert_called_once_with(mock_request)


def test_verify_token_with_user_auth(auth_middleware, mock_request):
    # Setup
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="user_token")
    auth_middleware._users.user_management_enabled.return_value = True
    auth_middleware._users.is_request_logged_in.return_value = True

    # Execute
    result = anyio.run(lambda: auth_middleware.verify_token(credentials, mock_request))

    # Verify
    assert result is None
    auth_middleware._users.is_request_logged_in.assert_called_once_with(mock_request)


def test_verify_token_no_credentials(auth_middleware, mock_request):
    # Setup
    auth_middleware._users.user_management_enabled.return_value = True

    # Execute and verify
    with pytest.raises(HTTPException) as excinfo:
        anyio.run(lambda: auth_middleware.verify_token(None, mock_request))

    # Verify
    assert excinfo.value.status_code == 401
    auth_middleware._users.is_request_logged_in.assert_not_called()


def test_verify_token_user_management_disabled(auth_middleware, mock_request):
    # Setup
    auth_middleware._users.user_management_enabled.return_value = False

    # Execute
    result = anyio.run(lambda: auth_middleware.verify_token(None, mock_request))

    # Verify
    assert result is None
    auth_middleware._users.is_request_logged_in.assert_not_called()


def test_verify_token_users_status_endpoint(auth_middleware, mock_request):
    # Setup
    mock_request.url.path = "/api/v1/config/users/status"

    # Execute
    result = anyio.run(lambda: auth_middleware.verify_token(None, mock_request))

    # Verify
    assert result is None
    auth_middleware._users.user_management_enabled.assert_not_called()
    auth_middleware._users.is_request_logged_in.assert_not_called()
