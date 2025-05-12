"""
Module for testing reservation service api
"""
import pytest
from httpx import AsyncClient
from fastapi import status


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


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


@pytest.mark.asyncio
async def test_get_public_reservation_services(client: AsyncClient):
    """
    Test retrieving a list of public reservation services.
    """
    response = await client.get("/reservation_services/services/public")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
