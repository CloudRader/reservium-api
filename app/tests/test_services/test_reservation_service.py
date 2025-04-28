"""
Module for testing reservation service ser.
"""
import pytest
from schemas import ReservationServiceUpdate
from api import PermissionDeniedException


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_create_reservation_service(reservation_service,
                                          reservation_service_create):
    """
    Test creating a reservation service.
    """
    assert reservation_service is not None
    assert reservation_service.name == reservation_service_create.name
    assert reservation_service.alias == reservation_service_create.alias
    assert reservation_service.web == reservation_service_create.web
    assert reservation_service.contact_mail == reservation_service_create.contact_mail
    assert reservation_service.public == reservation_service_create.public


@pytest.mark.asyncio
async def test_create_reservation_service_no_permission(service_reservation_service,
                                                        reservation_service_create,
                                                        user_not_head):
    """
    Test creating a reservation service when the user doesn't have permission.
    """
    with pytest.raises(PermissionDeniedException):
        await service_reservation_service.create_reservation_service(
            reservation_service_create, user_not_head
        )


@pytest.mark.asyncio
async def test_get_reservation_service(reservation_service,
                                       service_reservation_service):
    """
    Test getting a reservation service.
    """
    get_reservation_service = await service_reservation_service.get(
        reservation_service.id
    )
    assert get_reservation_service is not None
    assert get_reservation_service.name == reservation_service.name
    assert get_reservation_service.alias == reservation_service.alias


@pytest.mark.asyncio
async def test_get_reservation_service_by_name(reservation_service,
                                               service_reservation_service):
    """
    Test getting a reservation service by name.
    """
    get_reservation_service = await service_reservation_service.get_by_name(
        reservation_service.name
    )
    assert get_reservation_service is not None
    assert get_reservation_service.name == reservation_service.name
    assert get_reservation_service.alias == reservation_service.alias


@pytest.mark.asyncio
async def test_get_reservation_service_by_alias(reservation_service,
                                                service_reservation_service):
    """
    Test getting a reservation service by alias.
    """
    get_reservation_service = await service_reservation_service.get_by_alias(
        reservation_service.alias
    )
    assert get_reservation_service is not None
    assert get_reservation_service.name == reservation_service.name
    assert get_reservation_service.alias == reservation_service.alias


@pytest.mark.asyncio
async def test_get_public_reservation_service_empty(reservation_service,
                                                    service_reservation_service):
    """
    Test getting public reservation services with empty list.
    """
    get_reservation_service = await service_reservation_service.get_public_services()
    assert reservation_service is not None
    assert get_reservation_service == []


@pytest.mark.asyncio
async def test_get_public_reservation_service(reservation_service,
                                              service_reservation_service):
    """
    Test getting public reservation services.
    """
    await service_reservation_service.update(
        reservation_service.id, ReservationServiceUpdate(public=True)
    )
    get_reservation_service = await service_reservation_service.get_public_services()
    assert get_reservation_service is not None
    assert get_reservation_service[0].name == reservation_service.name
    assert get_reservation_service[0].alias == reservation_service.alias
    assert get_reservation_service[0].public == reservation_service.public


@pytest.mark.asyncio
async def test_update_reservation_service(service_reservation_service,
                                          reservation_service,
                                          user):
    """
    Test updating an existing reservation service.
    """
    reservation_service_update = ReservationServiceUpdate(
        name="Updated Game Room",
        alias="ngame"
    )

    assert reservation_service_update.web is None
    assert reservation_service_update.public is None

    updated_service = await service_reservation_service.update_reservation_service(
        reservation_service.id, reservation_service_update, user
    )

    assert updated_service is not None
    assert updated_service.name == reservation_service_update.name
    assert updated_service.alias == reservation_service_update.alias
    assert updated_service.web == reservation_service.web
    assert updated_service.contact_mail == reservation_service.contact_mail
    assert updated_service.public == reservation_service.public


@pytest.mark.asyncio
async def test_update_reservation_service_no_permission(service_reservation_service,
                                                        reservation_service,
                                                        user_not_head):
    """
    Test updating a reservation service when the user doesn't have permission.
    """
    reservation_service_update = ReservationServiceUpdate(
        name="Updated Game Room",
        alias="ngame",
    )

    with pytest.raises(PermissionDeniedException):
        await service_reservation_service.update_reservation_service(
            reservation_service.id, reservation_service_update, user_not_head
        )


@pytest.mark.asyncio
async def test_soft_delete_reservation_service(service_reservation_service,
                                               reservation_service,
                                               user):
    """
    Test soft deleting a reservation service.
    """
    soft_removed_service = await service_reservation_service.delete_reservation_service(
        reservation_service.id, user, hard_remove=False
    )

    assert soft_removed_service is not None
    assert soft_removed_service.id == reservation_service.id


@pytest.mark.asyncio
async def test_hard_delete_reservation_service(service_reservation_service,
                                               reservation_service,
                                               user):
    """
    Test hard deleting a reservation service.
    """
    hard_removed_service = await service_reservation_service.delete_reservation_service(
        reservation_service.id, user, hard_remove=True
    )

    assert hard_removed_service is not None
    assert hard_removed_service.id == reservation_service.id


@pytest.mark.asyncio
async def test_delete_reservation_service_no_permission(service_reservation_service,
                                                        reservation_service,
                                                        user_not_head):
    """
    Test deleting a reservation service when the user doesn't have permission.
    """
    with pytest.raises(PermissionDeniedException):
        await service_reservation_service.delete_reservation_service(
            reservation_service.id, user_not_head, hard_remove=False
        )
