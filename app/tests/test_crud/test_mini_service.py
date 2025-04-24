"""
Module for testing mini service crud
"""
import pytest
from schemas import MiniServiceUpdate


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_create_mini_service(test_mini_service):
    """
    Test creating a mini service.
    """
    assert test_mini_service.name == "Projector"


@pytest.mark.asyncio
async def test_get_mini_service_by_id(test_mini_service, mini_service_crud):
    """
    Test retrieving mini service by id.
    """
    mini_service = await mini_service_crud.get(test_mini_service.id)
    assert mini_service is not None
    assert mini_service.name == test_mini_service.name
    assert mini_service.id == test_mini_service.id
    assert mini_service.reservation_service_id == test_mini_service.reservation_service_id


@pytest.mark.asyncio
async def test_get_mini_service_by_name(test_mini_service, mini_service_crud):
    """
    Test retrieving mini service by name.
    """
    mini_service = await mini_service_crud.get_by_name(test_mini_service.name)
    assert mini_service is not None
    assert mini_service.id == test_mini_service.id
    assert (mini_service.reservation_service_id ==
            test_mini_service.reservation_service_id)


@pytest.mark.asyncio
async def test_get_all_mini_services(mini_service_crud,
                                     test_mini_service,
                                     test_mini_service2):
    """
    Test retrieving all mini services.
    """
    mini_service = await mini_service_crud.get_all()
    names = [service.name for service in mini_service]
    assert len(mini_service) >= 2
    assert test_mini_service.name in names
    assert test_mini_service2.name in names


@pytest.mark.asyncio
async def test_get_by_reservation_service_id(mini_service_crud, test_mini_service):
    """
    Test retrieving mini services by reservation service ID.
    """
    mini_services = await mini_service_crud.get_by_reservation_service_id(
        test_mini_service.reservation_service_id
    )
    assert any(mini_service.id == test_mini_service.id for mini_service in mini_services)


@pytest.mark.asyncio
async def test_get_names_by_reservation_service_id(mini_service_crud, test_mini_service):
    """
    Test retrieving mini service names by reservation service ID.
    """
    names = await mini_service_crud.get_names_by_reservation_service_id(
        test_mini_service.reservation_service_id
    )
    assert test_mini_service.name in names


@pytest.mark.asyncio
async def test_update_mini_service(test_mini_service, mini_service_crud):
    """
    Test updating mini service.
    """
    updated = await mini_service_crud.update(
        db_obj=test_mini_service,
        obj_in=MiniServiceUpdate(name="Console")
    )
    assert updated.name == "Console"


@pytest.mark.asyncio
async def test_soft_remove_mini_service(test_mini_service, mini_service_crud):
    """
    Test soft deleting mini service.
    """
    soft_removed = await mini_service_crud.soft_remove(test_mini_service.id)
    assert soft_removed.deleted_at is not None


@pytest.mark.asyncio
async def test_retrieve_soft_removed_mini_service(test_mini_service, mini_service_crud):
    """
    Test restoring soft deleted mini service.
    """
    await mini_service_crud.soft_remove(test_mini_service.id)
    restored = await mini_service_crud.retrieve_removed_object(test_mini_service.id)
    assert restored is not None
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_hard_remove_mini_service(test_mini_service, mini_service_crud):
    """
    Test permanently deleting mini service.
    """
    removed = await mini_service_crud.remove(test_mini_service.id)
    assert removed is not None

    should_be_none = await mini_service_crud.get(removed.id)
    assert should_be_none is None


@pytest.mark.asyncio
async def test_hard_remove_nonexistent_mini_service(test_mini_service, mini_service_crud):
    """
    Test deleting a nonexistent mini service.
    """
    removed = await mini_service_crud.remove(test_mini_service.id)
    assert removed is not None

    removed_none = await mini_service_crud.remove(test_mini_service.id)
    assert removed_none is None


@pytest.mark.asyncio
async def test_get_by_name_include_removed(mini_service_crud, test_mini_service):
    """
    Test retrieving a soft-deleted mini service by name with include_removed=True.
    """
    await mini_service_crud.soft_remove(test_mini_service.id)
    service = await mini_service_crud.get_by_name(
        name=test_mini_service.name,
        include_removed=True
    )
    assert service is not None
    assert service.deleted_at is not None


@pytest.mark.asyncio
async def test_get_by_id_include_removed(mini_service_crud, test_mini_service):
    """
    Test retrieving a soft-deleted mini service by ID with include_removed=True.
    """
    await mini_service_crud.soft_remove(test_mini_service.id)
    service = await mini_service_crud.get(
        uuid=test_mini_service.id,
        include_removed=True
    )
    assert service is not None
    assert service.deleted_at is not None
