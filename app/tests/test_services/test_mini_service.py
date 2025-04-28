"""
Module for testing mini service ser.
"""
import pytest
from schemas import MiniServiceUpdate
from api import PermissionDeniedException


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_create_mini_service(mini_service,
                                   mini_service_create):
    """
    Test creating a mini service.
    """
    assert mini_service is not None
    assert mini_service.name == mini_service_create.name
    assert (mini_service.reservation_service_id ==
            mini_service_create.reservation_service_id)


@pytest.mark.asyncio
async def test_create_mini_service_no_permission(service_mini_service,
                                                 mini_service_create,
                                                 user_not_head):
    """
    Test creating a mini service when the user doesn't have permission.
    """
    with pytest.raises(PermissionDeniedException):
        await service_mini_service.create_mini_service(
            mini_service_create, user_not_head
        )


@pytest.mark.asyncio
async def test_get_mini_service(service_mini_service,
                                mini_service):
    """
    Test getting a mini service.
    """
    get_mini_service = await service_mini_service.get(
        mini_service.id
    )
    assert get_mini_service is not None
    assert get_mini_service.name == mini_service.name
    assert (get_mini_service.reservation_service_id ==
            mini_service.reservation_service_id)


@pytest.mark.asyncio
async def test_get_mini_service_by_name(mini_service,
                                        service_mini_service):
    """
    Test getting a mini service by name.
    """
    get_mini_service = await service_mini_service.get_by_name(
        mini_service.name
    )
    assert get_mini_service is not None
    assert get_mini_service.name == mini_service.name
    assert (get_mini_service.reservation_service_id ==
            mini_service.reservation_service_id)


@pytest.mark.asyncio
async def test_get_mini_services_by_reservation_service_id(mini_service,
                                                           service_mini_service):
    """
    Test getting a mini service by reservation service id.
    """
    get_mini_services = await service_mini_service.get_by_reservation_service_id(
        mini_service.reservation_service_id
    )
    assert get_mini_services != []
    assert get_mini_services[0].name == mini_service.name
    assert (get_mini_services[0].reservation_service_id ==
            mini_service.reservation_service_id)


@pytest.mark.asyncio
async def test_update_mini_service(service_mini_service,
                                   mini_service,
                                   user):
    """
    Test updating an existing mini service.
    """
    mini_service_update = MiniServiceUpdate(
        name="Console",
    )

    updated_service = await service_mini_service.update_mini_service(
        mini_service.id, mini_service_update, user
    )

    assert updated_service is not None
    assert updated_service.name == mini_service_update.name
    assert updated_service.reservation_service_id == mini_service.reservation_service_id


@pytest.mark.asyncio
async def test_update_mini_service_no_permission(service_mini_service,
                                                 mini_service,
                                                 user_not_head):
    """
    Test updating a mini service when the user doesn't have permission.
    """
    mini_service_update = MiniServiceUpdate(
        name="Updated Bar",
    )

    with pytest.raises(PermissionDeniedException):
        await service_mini_service.update_mini_service(
            mini_service.id, mini_service_update, user_not_head
        )


@pytest.mark.asyncio
async def test_soft_delete_mini_service(service_mini_service,
                                        mini_service,
                                        user):
    """
    Test soft deleting a mini service.
    """
    soft_removed_service = await service_mini_service.delete_mini_service(
        mini_service.id, user, hard_remove=False
    )

    assert soft_removed_service is not None
    assert soft_removed_service.id == mini_service.id


@pytest.mark.asyncio
async def test_hard_delete_mini_service(service_mini_service,
                                        mini_service,
                                        user):
    """
    Test hard deleting a mini service.
    """
    hard_removed_service = await service_mini_service.delete_mini_service(
        mini_service.id, user, hard_remove=True
    )

    assert hard_removed_service is not None
    assert hard_removed_service.id == mini_service.id


@pytest.mark.asyncio
async def test_delete_mini_service_no_permission(service_mini_service,
                                                 mini_service,
                                                 user_not_head):
    """
    Test deleting a mini service when the user doesn't have permission.
    """
    with pytest.raises(PermissionDeniedException):
        await service_mini_service.delete_mini_service(
            mini_service.id, user_not_head, hard_remove=False
        )


@pytest.mark.asyncio
async def test_retrieve_soft_removed_mini_service(service_mini_service,
                                                  mini_service,
                                                  user):
    """
    Test restoring soft deleted mini service.
    """
    soft_removed_mini_service = await service_mini_service.delete_mini_service(
        mini_service.id, user, hard_remove=False
    )
    assert soft_removed_mini_service.deleted_at is not None
    restored = await service_mini_service.retrieve_removed_object(
        soft_removed_mini_service.id, user
    )
    assert restored is not None
    assert restored.deleted_at is None
