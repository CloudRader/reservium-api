"""Module for testing user api."""

from unittest.mock import patch

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
@patch("api.v2.auth.login")
async def test_get_is_redirect_uri(mock_login, is_auth_service, client: AsyncClient):
    """Test that /auth/login returns an authorization URL without hitting real OAuth server."""
    mock_login.return_value = "https://fake-auth-url"
    response = await client.get("/v2/auth/login")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == await is_auth_service.generate_is_oauth_redirect_uri()


@pytest.mark.asyncio
async def test_get_all_users_empty(client: AsyncClient):
    """Test that /users/ returns 403 when accessed without auth."""
    response = await client.get("/v2/users/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test that /users/logout logs out the user correctly."""
    response = await client.get("/v2/auth/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Logged out"}


# @pytest.mark.asyncio
# @patch("integrations.information_system.IsAuthService.get_token_response", new_callable=AsyncMock)
# @patch("api.authenticate_user", new_callable=AsyncMock)
# async def test_callback_success(
#     mock_authenticate_user,
#     mock_exchange_code,
#     client: AsyncClient,
# ):
#     """Test successful callback after OAuth authentication."""
#     mock_exchange_code.return_value = TokenResponse(
#         access_token="fake_token",
#         token_type="Bearer",
#         expires_in=3600,
#         scope="read write",
#     )
#     fake_user = type("User", (), {"username": "mocked_user"})()
#
#     mock_authenticate_user.return_value = fake_user
#
#     response = await client.get("/v2/auth/callback?code=1234")
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {"username": "mocked_user", "token_type": "bearer"}
