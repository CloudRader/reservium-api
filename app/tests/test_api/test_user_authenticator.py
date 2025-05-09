"""
Module for testing user authenticator api
"""
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi import HTTPException, status
from api import get_oauth_session, get_request, authenticate_user, \
    get_current_token, get_current_user


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


# pylint: disable=too-few-public-methods
# reason: It needs for testing
class DummyRequest:
    """
    Dummy request object for testing session-based access.
    """
    def __init__(self, session_data):
        self.session = session_data


def test_get_oauth_session():
    """
    Test that OAuth session is configured properly.
    """
    session = get_oauth_session()
    assert session.client_id is not None
    assert session.redirect_uri is not None


@pytest.mark.asyncio
@patch("api.user_authenticator.httpx.AsyncClient.get")
async def test_get_request_success(mock_get):
    """
    Test successful HTTPX get request returns parsed JSON.
    """
    mock_response = MagicMock()
    mock_response.status_code = status.HTTP_200_OK
    mock_response.json.return_value = {"data": "ok"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = await get_request("dummy_token", "/test-endpoint")
    assert result == {"data": "ok"}


@pytest.mark.asyncio
@patch("api.user_authenticator.get_request")
async def test_authenticate_user(mock_get_request, user_data_from_is,
                                 room_data_from_is):
    """
    Test user authentication flow with mocked data from identity service.
    """
    mock_get_request.return_value = {"some": "response"}
    mock_user_service = AsyncMock()
    mock_user_service.create_user.return_value = "mocked_user"

    mock_get_request.side_effect = [
        user_data_from_is.model_dump(),  # /users/me
        [],  # /user_roles/mine
        [],  # /services/mine
        room_data_from_is.model_dump() # /rooms/mine
    ]

    user = await authenticate_user(mock_user_service, token="dummy")
    assert user == "mocked_user"


@pytest.mark.asyncio
async def test_get_current_token_success():
    """
    Test extracting access token from request session.
    """
    request = DummyRequest({"oauth_token": {"access_token": "abc"}})
    token = await get_current_token(request)
    assert token == "abc"


@pytest.mark.asyncio
async def test_get_current_token_missing():
    """
    Test missing access token in session raises HTTPException.
    """
    request = DummyRequest({})
    with pytest.raises(HTTPException):
        await get_current_token(request)


@pytest.mark.asyncio
@patch("api.user_authenticator.get_request")
async def test_get_current_user_success(mock_get_request, user_data_from_is):
    """
    Test retrieval of current user from session and database.
    """
    mock_user_service = AsyncMock()
    mock_user_service.get_by_username.return_value = {"id": 1, "username": "user1"}

    mock_get_request.return_value = user_data_from_is.model_dump()

    request = DummyRequest({
        "user_username": "user1",
        "oauth_token": {"access_token": "abc"}
    })

    user = await get_current_user(mock_user_service, request)
    assert user["username"] == "user1"


@pytest.mark.asyncio
async def test_get_current_user_no_username():
    """
    Test that missing username in session raises HTTPException.
    """
    mock_user_service = AsyncMock()
    request = DummyRequest({})  # no session
    with pytest.raises(HTTPException):
        await get_current_user(mock_user_service, request)
