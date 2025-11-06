"""Module for testing event model."""

import pytest
from datetime import datetime
from core.models import EventModel, EventState


@pytest.mark.asyncio
async def test_create_event(test_event, test_user, test_calendar):
    """Test creating an Event ORM object."""
    assert test_event.id is not None
    assert test_event.purpose == "Test Event"
    assert test_event.guests == 10
    assert test_event.email == "user@example.com"
    assert test_event.event_state == EventState.NOT_APPROVED
    assert test_event.user_id == test_user.id
    assert test_event.calendar_id == test_calendar.id
    assert isinstance(test_event.reservation_start, datetime)
    assert isinstance(test_event.reservation_end, datetime)


@pytest.mark.asyncio
async def test_get_event(async_session, test_event):
    """Test fetching an event from the database."""
    db_obj = await async_session.get(EventModel, test_event.id)
    assert db_obj is not None
    assert db_obj.purpose == test_event.purpose
    assert db_obj.guests == test_event.guests


@pytest.mark.asyncio
async def test_update_event(async_session, test_event):
    """Test updating event fields."""
    test_event.purpose = "Updated Event"
    test_event.guests = 20
    await async_session.commit()
    await async_session.refresh(test_event)
    assert test_event.purpose == "Updated Event"
    assert test_event.guests == 20


@pytest.mark.asyncio
async def test_delete_event(async_session, test_event):
    """Test deleting an event."""
    await async_session.delete(test_event)
    await async_session.commit()
    deleted = await async_session.get(EventModel, test_event.id)
    assert deleted is None
