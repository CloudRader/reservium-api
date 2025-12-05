"""Module for testing calendar service crud."""

import pytest
from core.schemas import CalendarUpdate


@pytest.mark.asyncio
async def test_create_calendar(test_calendar):
    """Test creating a calendar."""
    assert test_calendar.reservation_type == "Grillcentrum"
    assert test_calendar.id == "fixteure.calen.id@exgogl.eu"
    assert test_calendar.max_people == 15
    assert test_calendar.club_member_rules.night_time is True


@pytest.mark.asyncio
async def test_get_calendar_by_id(test_calendar, calendar_crud):
    """Test retrieving calendar by ID."""
    calendar = await calendar_crud.get(test_calendar.id)
    assert calendar is not None
    assert calendar.id == test_calendar.id
    assert calendar.reservation_service_id == test_calendar.reservation_service_id


@pytest.mark.asyncio
async def test_get_calendar_by_reservation_type(test_calendar, calendar_crud):
    """Test retrieving calendar by reservation type."""
    calendar = await calendar_crud.get_by_reservation_type(
        reservation_type=test_calendar.reservation_type,
    )
    assert calendar is not None
    assert calendar.id == test_calendar.id


@pytest.mark.asyncio
async def test_get_all_calendars(test_calendar, test_calendar2, calendar_crud):
    """Test retrieving all calendars."""
    calendars = await calendar_crud.get_all()
    assert any(cal.id == test_calendar.id for cal in calendars)
    assert test_calendar != test_calendar2


@pytest.mark.asyncio
async def test_get_with_collisions(test_calendar, test_calendar2, calendar_crud):
    """Test getting calendar with collisions."""
    calendar = await calendar_crud.get_with_collisions(test_calendar2.id)
    assert calendar.collisions[0] == test_calendar


@pytest.mark.asyncio
async def test_update_calendar(test_calendar, test_calendar2, test_mini_service, calendar_crud):
    """Test updating a calendar."""
    updated = await calendar_crud.update_with_mini_services_and_collisions(
        db_obj=test_calendar2,
        obj_in=CalendarUpdate(color="#ff0000", collision_ids=[test_calendar.id]),
        mini_services=[test_mini_service],
    )
    assert updated.color == "#ff0000"
    assert updated.mini_services[0] == test_mini_service


@pytest.mark.asyncio
async def test_soft_remove_calendar(test_calendar, calendar_crud):
    """Test soft deleting calendar."""
    soft_removed = await calendar_crud.soft_remove(test_calendar)
    assert soft_removed.deleted_at is not None


@pytest.mark.asyncio
async def test_retrieve_soft_removed_calendar(test_calendar, calendar_crud):
    """Test restoring soft deleted calendar."""
    await calendar_crud.soft_remove(test_calendar)
    restored = await calendar_crud.restore(test_calendar)
    assert restored is not None
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_hard_remove_calendar(test_calendar, calendar_crud):
    """Test permanently deleting calendar."""
    removed = await calendar_crud.remove(test_calendar.id)
    assert removed is not None

    should_be_none = await calendar_crud.get(removed.id)
    assert should_be_none is None


@pytest.mark.asyncio
async def test_get_by_id_include_removed(test_calendar, calendar_crud):
    """Test retrieving a soft-deleted calendar by ID with include_removed=True."""
    await calendar_crud.soft_remove(test_calendar)
    calendar = await calendar_crud.get(test_calendar.id, include_removed=True)
    assert calendar is not None
    assert calendar.deleted_at is not None


@pytest.mark.asyncio
async def test_get_by_reservation_type_include_removed(
    test_calendar,
    calendar_crud,
):
    """Test retrieving a soft-deleted calendar by reservation type with include_removed=True."""
    await calendar_crud.soft_remove(test_calendar)
    calendar = await calendar_crud.get_by_reservation_type(
        reservation_type=test_calendar.reservation_type,
        include_removed=True,
    )
    assert calendar is not None
    assert calendar.deleted_at is not None
