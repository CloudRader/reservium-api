"""
Module for testing calendar service crud
"""
import pytest
from schemas import CalendarUpdate


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_create_calendar(test_calendar_service):
    """
    Test creating a calendar.
    """
    assert test_calendar_service.reservation_type == "Grillcentrum"
    assert test_calendar_service.id == "fixteure.calen.id@exgogl.eu"
    assert test_calendar_service.max_people == 15
    assert test_calendar_service.club_member_rules.night_time is True
    assert test_calendar_service.mini_services == ["Console", "Bar", "Projector"]


@pytest.mark.asyncio
async def test_get_calendar_by_id(test_calendar_service, calendar_crud):
    """
    Test retrieving calendar by ID.
    """
    calendar = await calendar_crud.get(test_calendar_service.id)
    assert calendar is not None
    assert calendar.id == test_calendar_service.id
    assert calendar.reservation_service_id == test_calendar_service.reservation_service_id


@pytest.mark.asyncio
async def test_get_calendar_by_reservation_type(test_calendar_service, calendar_crud):
    """
    Test retrieving calendar by reservation type.
    """
    calendar = await calendar_crud.get_by_reservation_type(
        reservation_type=test_calendar_service.reservation_type
    )
    assert calendar is not None
    assert calendar.id == test_calendar_service.id


@pytest.mark.asyncio
async def test_get_all_calendars(test_calendar_service, calendar_crud):
    """
    Test retrieving all calendars.
    """
    calendars = await calendar_crud.get_all()
    assert any(cal.id == test_calendar_service.id for cal in calendars)


@pytest.mark.asyncio
async def test_get_by_reservation_service_id(calendar_crud, test_calendar_service):
    """
    Test retrieving calendars by reservation service ID.
    """
    calendars = await calendar_crud.get_by_reservation_service_id(
        test_calendar_service.reservation_service_id
    )
    assert any(cal.id == test_calendar_service.id for cal in calendars)


@pytest.mark.asyncio
async def test_update_calendar(calendar_crud, test_calendar_service):
    """
    Test updating a calendar.
    """
    updated = await calendar_crud.update(
        db_obj=test_calendar_service,
        obj_in=CalendarUpdate(color="#ff0000")
    )
    assert updated.color == "#ff0000"


@pytest.mark.asyncio
async def test_soft_remove_calendar(calendar_crud, test_calendar_service):
    """
    Test soft deleting calendar.
    """
    soft_removed = await calendar_crud.soft_remove(test_calendar_service.id)
    assert soft_removed.deleted_at is not None


@pytest.mark.asyncio
async def test_retrieve_soft_removed_calendar(calendar_crud, test_calendar_service):
    """
    Test restoring soft deleted calendar.
    """
    await calendar_crud.soft_remove(test_calendar_service.id)
    restored = await calendar_crud.retrieve_removed_object(test_calendar_service.id)
    assert restored is not None
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_hard_remove_calendar(calendar_crud, test_calendar_service):
    """
    Test permanently deleting calendar.
    """
    removed = await calendar_crud.remove(test_calendar_service.id)
    assert removed is not None

    should_be_none = await calendar_crud.get(removed.id)
    assert should_be_none is None


@pytest.mark.asyncio
async def test_hard_remove_nonexistent_calendar(calendar_crud, test_calendar_service):
    """
    Test deleting a nonexistent calendar.
    """
    removed = await calendar_crud.remove(test_calendar_service.id)
    assert removed is not None

    removed_none = await calendar_crud.remove(test_calendar_service.id)
    assert removed_none is None


@pytest.mark.asyncio
async def test_get_by_id_include_removed(calendar_crud, test_calendar_service):
    """
    Test retrieving a soft-deleted calendar by ID with include_removed=True.
    """
    await calendar_crud.soft_remove(test_calendar_service.id)
    calendar = await calendar_crud.get(
        test_calendar_service.id,
        include_removed=True
    )
    assert calendar is not None
    assert calendar.deleted_at is not None


@pytest.mark.asyncio
async def test_get_by_reservation_type_include_removed(calendar_crud, test_calendar_service):
    """
    Test retrieving a soft-deleted calendar by reservation type with include_removed=True.
    """
    await calendar_crud.soft_remove(test_calendar_service.id)
    calendar = await calendar_crud.get_by_reservation_type(
        reservation_type=test_calendar_service.reservation_type,
        include_removed=True
    )
    assert calendar is not None
    assert calendar.deleted_at is not None
