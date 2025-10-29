"""Module for testing calendar model."""

import pytest
import sqlalchemy
from core.models import CalendarModel


@pytest.mark.asyncio
async def test_create_calendar(test_calendar, test_reservation_service):
    """Test creating a calendar."""
    assert test_calendar.id == "test_calendar@google.com"
    assert test_calendar.reservation_type == "Entire Space"
    assert test_calendar.max_people == 10
    assert test_calendar.color == "#00ffcc"
    assert test_calendar.club_member_rules.night_time is False
    assert test_calendar.reservation_service_id == test_reservation_service.id


@pytest.mark.asyncio
async def test_get_calendar(async_session, test_calendar):
    """Test fetching calendar from the database."""
    db_obj = await async_session.get(CalendarModel, test_calendar.id)
    assert db_obj is not None
    assert db_obj.reservation_type == test_calendar.reservation_type


@pytest.mark.asyncio
async def test_update_calendar(async_session, test_calendar):
    """Test updating calendar values."""
    test_calendar.color = "#123456"
    await async_session.commit()
    await async_session.refresh(test_calendar)
    assert test_calendar.color == "#123456"
    assert test_calendar.max_people == 10


@pytest.mark.asyncio
async def test_delete_calendar(async_session, test_calendar):
    """Test soft-deleting the calendar (or real delete if no soft delete)."""
    await async_session.delete(test_calendar)
    await async_session.commit()
    deleted = await async_session.get(CalendarModel, test_calendar.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_list_calendars(
    async_session,
    rules_club_member,
    test_reservation_service,
    test_mini_service,
):
    """Test listing multiple calendars."""
    calendars = [
        CalendarModel(
            id="test_calwagwagwgwandar_type1@exam.com",
            reservation_type="type1blan",
            color="#ba0201",
            max_people=10,
            more_than_max_people_with_permission=True,
            collision_with_itself=False,
            club_member_rules=rules_club_member,
            active_member_rules=rules_club_member,
            manager_rules=rules_club_member,
            reservation_service_id=test_reservation_service.id,
            mini_services=[test_mini_service],
        ),
        CalendarModel(
            id="test_calendar_type2@google.com",
            reservation_type="type2",
            color="#bbccdd",
            max_people=20,
            more_than_max_people_with_permission=True,
            collision_with_itself=False,
            club_member_rules=rules_club_member,
            active_member_rules=rules_club_member,
            manager_rules=rules_club_member,
            reservation_service_id=test_reservation_service.id,
            mini_services=[test_mini_service],
        ),
    ]
    async_session.add_all(calendars)
    await async_session.commit()

    result = (await async_session.execute(sqlalchemy.select(CalendarModel))).scalars().all()

    assert len(result) >= 2
    reservation_types = [c.reservation_type for c in result]
    assert "type1blan" in reservation_types
    assert "type2" in reservation_types


def test_collision_ids_empty(rules_club_member):
    """Test that collision_ids returns an empty list if no collisions exist."""
    cal = CalendarModel(
        id="cal_1",
        reservation_type="Type1",
        color="#fff",
        max_people=10,
        club_member_rules=rules_club_member,
        active_member_rules=rules_club_member,
        manager_rules=rules_club_member,
        reservation_service_id="res_1",
    )
    assert cal.collision_ids == []


def test_collision_ids_with_collisions(rules_club_member):
    """Test that collision_ids returns the IDs of all colliding calendars."""
    cal1 = CalendarModel(
        id="cal_1",
        reservation_type="Type1",
        color="#fff",
        max_people=10,
        club_member_rules=rules_club_member,
        active_member_rules=rules_club_member,
        manager_rules=rules_club_member,
        reservation_service_id="res_1",
    )
    cal2 = CalendarModel(
        id="cal_2",
        reservation_type="Type2",
        color="#000",
        max_people=20,
        club_member_rules=rules_club_member,
        active_member_rules=rules_club_member,
        manager_rules=rules_club_member,
        reservation_service_id="res_1",
    )
    cal3 = CalendarModel(
        id="cal_3",
        reservation_type="Type3",
        color="#123",
        max_people=5,
        club_member_rules=rules_club_member,
        active_member_rules=rules_club_member,
        manager_rules=rules_club_member,
        reservation_service_id="res_1",
    )

    # Assign collisions manually
    cal1.collisions = [cal2, cal3]

    assert set(cal1.collision_ids) == {"cal_2", "cal_3"}
