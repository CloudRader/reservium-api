"""
Module for testing calendar crud
"""
import pytest

from crud import CRUDCalendar


# Using fixtures as variables is a standard for pytest
# pylint: disable=redefined-outer-name

@pytest.fixture()
def calendar_crud(db_session):
    """
    Return calendar crud.
    """
    return CRUDCalendar(db=db_session)


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
    calendar_to_update = calendar_crud.get_by_calendar_id(calendar.calendar_id)
    calendar_updated = calendar_crud.update(db_obj=calendar_to_update,
                                            obj_in=calendar_update)

    assert calendar_updated is not None
    assert calendar_updated.max_people == calendar_update.max_people
