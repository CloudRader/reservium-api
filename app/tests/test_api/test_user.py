"""
Module for testing user api
"""
from unittest.mock import patch, AsyncMock

import pytest
from httpx import AsyncClient
from fastapi import status


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_get_auth_code(client: AsyncClient):
    """
    Fixture to initiate the login process and get the auth code.
    """
    auth_code = await client.get("/users/login")
    assert auth_code.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_all_users_empty(client: AsyncClient):
    """
    Test that /users/ returns 404 when there are no users in the database.
    """
    response = await client.get("/users/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'message': 'No users in db.'}


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """
    Test that /users/logout logs out the user correctly.
    """
    response = await client.get("/users/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Logged out"}


@pytest.mark.asyncio
@patch("api.users.get_oauth_session")
async def test_login(mock_get_oauth, client: AsyncClient):
    """
    Test that /users/login redirects to an OAuth authorization URL.
    """
    mock_session = mock_get_oauth.return_value
    mock_session.authorization_url.return_value = ("https://fake-auth-url", "fake_state")

    response = await client.get("/users/login")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().startswith("https://fake-auth-url")


@pytest.mark.asyncio
@patch("api.users.get_oauth_session")
@patch("api.users.authenticate_user", new_callable=AsyncMock)
async def test_callback_success(mock_authenticate_user, mock_get_oauth, client: AsyncClient):
    """
    Test successful callback after OAuth authentication.
    """
    fake_token = {"access_token": "fake_token"}
    fake_user = type("User", (), {"username": "mocked_user"})()

    mock_session = mock_get_oauth.return_value
    mock_session.fetch_token.return_value = fake_token
    mock_authenticate_user.return_value = fake_user

    response = await client.get("/users/callback?code=1234")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"username": "mocked_user", "token_type": "bearer"}
