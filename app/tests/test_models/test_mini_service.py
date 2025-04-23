"""
Module for testing mini service model
"""
import uuid
from models import MiniServiceModel
import sqlalchemy
import pytest


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_create_mini_service(test_mini_service,
                                   create_mini_service_uuid,
                                   create_reservation_service_uuid):
    """
    Test creating mini service model.
    """
    assert test_mini_service.id == create_mini_service_uuid
    assert test_mini_service.name == "Bar"
    assert test_mini_service.reservation_service_id == create_reservation_service_uuid


@pytest.mark.asyncio
async def test_get_mini_service(async_session, test_mini_service):
    """
    Test retrieving the mini service from the database.
    """
    db_obj = await async_session.get(MiniServiceModel, test_mini_service.id)
    assert db_obj is not None
    assert db_obj.name == test_mini_service.name


@pytest.mark.asyncio
async def test_update_mini_service(async_session, test_mini_service):
    """
    Test updating the mini service.
    """
    test_mini_service.name = "Updated Mini"
    await async_session.commit()
    await async_session.refresh(test_mini_service)
    assert test_mini_service.name == "Updated Mini"


@pytest.mark.asyncio
async def test_delete_mini_service(async_session, test_mini_service):
    """
    Test deleting the mini service.
    """
    await async_session.delete(test_mini_service)
    await async_session.commit()
    deleted = await async_session.get(MiniServiceModel, test_mini_service.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_list_mini_services(async_session, test_reservation_service):
    """
    Test listing multiple mini services.
    """
    services = [
        MiniServiceModel(
            id=uuid.uuid4(),
            name="Mini A",
            reservation_service_id=test_reservation_service.id
        ),
        MiniServiceModel(
            id=uuid.uuid4(),
            name="Mini B",
            reservation_service_id=test_reservation_service.id
        ),
    ]
    async_session.add_all(services)
    await async_session.commit()

    result = (await async_session.execute(
        sqlalchemy.select(MiniServiceModel)
    )).scalars().all()

    assert len(result) == 2
    names = [s.name for s in result]
    assert "Mini A" in names
    assert "Mini B" in names
