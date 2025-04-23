"""
Module for testing reservation service model
"""
import uuid
from models import ReservationServiceModel
import sqlalchemy
import pytest


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_create_reservation_service(test_reservation_service,
                                          create_reservation_service_uuid):
    """
    Test creating reservation service model.
    """
    assert test_reservation_service.id == create_reservation_service_uuid
    assert test_reservation_service.name == "Club Room"
    assert test_reservation_service.alias == "club"
    assert test_reservation_service.public is True
    assert test_reservation_service.web == "test@example.com"
    assert test_reservation_service.contact_mail == "club.room.test@buk.cvut.cz"


@pytest.mark.asyncio
async def test_get_reservation_service(async_session, test_reservation_service):
    """
    Test getting the reservation service from the database.
    """
    db_obj = await async_session.get(ReservationServiceModel, test_reservation_service.id)
    assert db_obj is not None
    assert db_obj.name == test_reservation_service.name


@pytest.mark.asyncio
async def test_update_reservation_service(async_session, test_reservation_service):
    """
    Test updating the reservation service.
    """
    test_reservation_service.name = "Updated Room"
    await async_session.commit()
    await async_session.refresh(test_reservation_service)
    assert test_reservation_service.name == "Updated Room"


@pytest.mark.asyncio
async def test_delete_reservation_service(async_session, test_reservation_service):
    """
    Test deleting the reservation service.
    """
    await async_session.delete(test_reservation_service)
    await async_session.commit()
    deleted = await async_session.get(ReservationServiceModel, test_reservation_service.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_list_reservation_services(async_session):
    """
    Test listing multiple reservation services.
    """
    services = [
        ReservationServiceModel(
            id=uuid.uuid4(),
            name="Room A",
            alias="room_a",
            public=True,
            web="a@example.com",
            contact_mail="rooma@buk.cvut.cz"
        ),
        ReservationServiceModel(
            id=uuid.uuid4(),
            name="Room B",
            alias="room_b",
            public=False,
            web="b@example.com",
            contact_mail="roomb@buk.cvut.cz"
        ),
    ]
    async_session.add_all(services)
    await async_session.commit()

    result = (await async_session.execute(
        sqlalchemy.select(ReservationServiceModel)
    )).scalars().all()

    assert len(result) == 2
    names = [s.name for s in result]
    assert "Room A" in names
    assert "Room B" in names
