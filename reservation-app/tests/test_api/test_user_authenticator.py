"""Module for testing user authenticator api."""
#
# from unittest.mock import AsyncMock, MagicMock, patch
#
# import pytest
# from api import (
#     authenticate_user,
#     get_current_user,
# )
# from fastapi import HTTPException, status
# from fastapi.security import HTTPAuthorizationCredentials
#
#
# @pytest.mark.asyncio
# @patch("integrations.information_system.IsService._get_request", new_callable=AsyncMock)
# async def test_get_request_success(mock_get, is_service):
#     """Test successful HTTPX get request returns parsed JSON."""
#     mock_response = MagicMock()
#     mock_response.status_code = status.HTTP_200_OK
#     mock_response.json.return_value = {"data": "ok"}
#     mock_response.raise_for_status.return_value = None
#     mock_get.return_value = mock_response
#
#     result = await is_service.get_user_data("dummy_token")
#     assert result == {"data": "ok"}
#
#
# @pytest.mark.asyncio
# @patch("integrations.information_system.IsService._get_request", new_callable=AsyncMock)
# async def test_authenticate_user(
#     mock_get_request,
#     user_data_from_is,
#     room_data_from_is,
# ):
#     """Test user authentication flow with mocked data from identity service."""
#     mock_user_service = AsyncMock()
#     mock_user_service.create_user.return_value = "mocked_user"
#     mock_is_service = AsyncMock()
#
#     mock_get_request.side_effect = [
#         user_data_from_is.model_dump(),  # /users/me
#         [],  # /user_roles/mine
#         [],  # /services/mine
#         room_data_from_is.model_dump(),  # /rooms/mine
#     ]
#
#     user = await authenticate_user(mock_user_service, mock_is_service, token="dummy")
#     assert user == "mocked_user"
#
#
# @pytest.mark.asyncio
# @patch("api.user_authenticator.get_request")
# async def test_get_current_user_success(mock_get_request, user_data_from_is):
#     """Test retrieval of current user from session and database."""
#     mock_get_request.return_value = user_data_from_is.model_dump()
#
#     mock_user_service = AsyncMock()
#     mock_is_service = AsyncMock()
#     mock_user_service.get.return_value = {
#         "id": user_data_from_is.id,
#         "username": user_data_from_is.username,
#     }
#     creds = HTTPAuthorizationCredentials(
#         scheme="Bearer",
#         credentials="dummy_token",
#     )
#
#
#     user = await get_current_user(mock_user_service, mock_is_service, creds)
#     assert user["username"] == user_data_from_is.username
#
#
# @pytest.mark.asyncio
# async def test_get_current_user_no_token():
#     """Test that missing token raises HTTPException."""
#     mock_user_service = AsyncMock()
#     mock_is_service = AsyncMock()
#     creds = HTTPAuthorizationCredentials(
#         scheme="Bearer",
#         credentials="None",
#     )
#     with pytest.raises(HTTPException) as exc_info:
#         await get_current_user(mock_user_service, mock_is_service, token=creds)
#     assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
#
#
# @pytest.mark.asyncio
# @patch("api.user_authenticator.get_request")
# async def test_get_current_user_not_found(mock_get_request, user_data_from_is):
#     """Test that unknown user raises HTTPException."""
#     mock_get_request.return_value = user_data_from_is.model_dump()
#
#     mock_user_service = AsyncMock()
#     mock_is_service = AsyncMock()
#     mock_user_service.get.return_value = None  # user not found
#     creds = HTTPAuthorizationCredentials(
#         scheme="Bearer",
#         credentials="dummy_token",
#     )
#
#     with pytest.raises(HTTPException) as exc_info:
#         await get_current_user(mock_user_service, mock_is_service, token=creds)
#     assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
