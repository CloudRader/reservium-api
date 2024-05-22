"""
Module for testing calendar crud
"""
import pytest

from crud import CRUDCalendar
from schemas import CalendarCreate, CalendarUpdate
import crud
import schemas
import models


# Using fixtures as variables is a standard for pytest
# pylint: disable=redefined-outer-name

@pytest.fixture()
def calendar_crud(db_session):
    """
    Return calendar crud.
    """
    return CRUDCalendar(db=db_session)


@pytest.fixture()
def calendar_create() -> CalendarCreate:
    """
    Return new calendar.
    """
    rules = {
        "night_time": False,
        "reservation_more_24_hours": False,
        "in_advance_hours": 24,
        "in_advance_minutes": 14,
        "in_advance_day": 14
    }
    return CalendarCreate(
        calendar_id="c_f8a87bad9df63841a343835e6c55964349",
        service_alias="klub",
        reservation_type="Table Soccer",
        event_name="Stolní Fotbal/Table Soccer",
        max_people=6,
        collision_with_itself=False,
        club_member_rules=rules,
        active_member_rules=rules,
        manager_rules=rules,
    )


@pytest.fixture()
def calendar_update() -> CalendarUpdate:
    """
    Return new CalendarUpdate schema.
    """
    return CalendarUpdate(
        max_people=10,
    )


def test_create_calendar(calendar_crud, calendar_create):
    """
    Test creating calendar.
    """
    calendar = calendar_crud.create(obj_in=calendar_create)
    assert calendar is not None


def test_get_created_calendar(calendar_crud, calendar_create):
    """
    Test getting created calendar.
    """
    db_calendar = calendar_crud.get(calendar_create.calendar_id)
    assert db_calendar is not None


def test_delete_calendar(calendar_crud, calendar_create):
    """
    Test deleting calendar.
    """
    removed_calendar = calendar_crud.remove(calendar_create.calendar_id)
    assert removed_calendar is not None
    assert removed_calendar.calendar_id == calendar_create.calendar_id
    db_calendar = calendar_crud.get(removed_calendar.calendar_id)
    assert db_calendar is None


def test_remove_nonexistent_calendar(calendar_crud, calendar_create):
    """
    Test deleting nonexistent calendar.
    """
    calendar = calendar_crud.create(obj_in=calendar_create)
    calendar_removed = calendar_crud.remove(calendar.calendar_id)
    assert calendar_removed is not None
    calendar_removed = calendar_crud.remove(calendar_removed.calendar_id)
    assert calendar_removed is None
    calendar_removed = calendar_crud.remove(None)
    assert calendar_removed is None


def test_update_calendar(calendar_crud, calendar_create,
                         calendar_update):
    """
    Test updating calendar.
    """
    calendar = calendar_crud.create(obj_in=calendar_create)
    assert calendar is not None
    calendar_updated = calendar_crud.update(db_obj=calendar, obj_in=calendar_update)
    assert calendar_updated is not None
