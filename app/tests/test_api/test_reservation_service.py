"""
Module for testing reservation service api
"""
import pytest
from httpx import AsyncClient
from fastapi import status


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


# @pytest.mark.asyncio
# @patch("api.user_authenticator.get_request")
# async def test_create_reservation_service(mock_get_request,
#                                           authorized_client: AsyncClient,
#                                           user_data_from_is):
#     mock_get_request.return_value = user_data_from_is.model_dump()
#
#     payload = {
#         "name": "Sample Room",
#         "alias": "sroom",
#         "web": "https://example.com",
#         "contact_mail": "contact@example.com",
#         "public": True
#     }
#     # response = await client.post(
#     #     "/reservation_services/create_reservation_service",
#     #     json=payload,
#     #     headers={"Authorization": f"Bearer {authorized_user.token}"}
#     # )
#     response = await authorized_client.post(
#         "/reservation_services/create_reservation_service",
#         json=payload
#     )
#
#     assert response.status_code == status.HTTP_200_OK
#     data = response.json()
#     assert data["name"] == payload["name"]


@pytest.mark.asyncio
async def test_get_reservation_service(client: AsyncClient, reservation_service):
    """
    Test retrieving a single reservation service by its ID.
    """
    response = await client.get(
        f"/reservation_services/{reservation_service.id}"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(reservation_service.id)


# @pytest.mark.asyncio
# async def test_get_all_reservation_services(client: AsyncClient, reservation_service):
#     response = await client.get(
#         "/reservation_services/"
#     )
#     assert response.status_code == status.HTTP_200_OK
#     assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_public_reservation_services(client: AsyncClient):
    """
    Test retrieving a list of public reservation services.
    """
    response = await client.get("/reservation_services/services/public")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

# @pytest.mark.asyncio
# async def test_update_reservation_service(async_client: AsyncClient,
#                                           authorized_user, reservation_service):
#     update_payload = {"note": "Updated note"}
#     response = await async_client.put(
#         f"/reservation_services/{reservation_service.id}",
#         json=update_payload,
#         headers={"Authorization": f"Bearer {authorized_user.token}"}
#     )
#     assert response.status_code == 200
#     assert response.json()["note"] == "Updated note"


# @pytest.mark.asyncio
# async def test_retrieve_deleted_reservation_service(async_client: AsyncClient, authorized_user,
#                                                     deleted_reservation_service):
#     response = await async_client.put(
#         f"/reservation_services/retrieve_deleted/{deleted_reservation_service.id}",
#         headers={"Authorization": f"Bearer {authorized_user.token}"}
#     )
#     assert response.status_code == 200
#     assert response.json()["id"] == str(deleted_reservation_service.id)
#
#
# @pytest.mark.asyncio
# async def test_delete_reservation_service(async_client: AsyncClient,
#                                           authorized_user, reservation_service):
#     response = await async_client.delete(
#         f"/reservation_services/{reservation_service.id}",
#         headers={"Authorization": f"Bearer {authorized_user.token}"}
#     )
#     assert response.status_code == 200
#     assert response.json()["id"] == str(reservation_service.id)
#
#
# @pytest.mark.asyncio
# async def test_get_reservation_service_by_name(async_client: AsyncClient, reservation_service):
#     response = await async_client.get(f"/reservation_services/name/{reservation_service.name}")
#     assert response.status_code == 200
#     assert response.json()["name"] == reservation_service.name
#
#
# @pytest.mark.asyncio
# async def test_get_reservation_service_by_alias(async_client: AsyncClient, reservation_service):
#     response = await async_client.get(f"/reservation_services/alias/{reservation_service.alias}")
#     assert response.status_code == 200
#     assert response.json()["alias"] == reservation_service.alias
