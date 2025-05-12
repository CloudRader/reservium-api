"""
Tests for MiniService Pydantic Schemas
"""
import pytest
from pydantic import ValidationError
from models import EventState
from schemas.event import (
    EventCreateToDb,
    EventUpdate,
    EventInDBBase,
    Event,
)


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


def test_event_create_valid():
    """
    Test creating an event with valid data.
    """
    schema = EventCreateToDb(
        id="some_id_string",
        purpose="Birthday party",
        guests=5,
        email="coolEmail@buk.cvut.cz",
        start_datetime="2025-05-12T11:00",
        end_datetime="2025-05-12T16:00",
        event_state=EventState.CONFIRMED,
        user_id=21412,
        calendar_id="wfwafwjag2@goog.com",
    )
    assert schema.purpose == "Birthday party"
    assert schema.calendar_id == "wfwafwjag2@goog.com"
    assert schema.guests == 5
    assert schema.event_state == EventState.CONFIRMED
    assert schema.user_id == 21412


def test_event_update_partial():
    """
    Test updating event with partial data.
    """
    update = EventUpdate(purpose="New Purpose")
    assert update.purpose == "New Purpose"


def test_event_in_db_base_schema():
    """
    Test full event DB representation.
    """

    schema = EventInDBBase(
        id="some_id_string",
        purpose="Birthday party",
        guests=5,
        email="coolEmail@buk.cvut.cz",
        start_datetime="2025-05-12T11:00",
        end_datetime="2025-05-12T16:00",
        event_state=EventState.CONFIRMED,
        user_id=21412,
        calendar_id="wfwafwjag2@goog.com",
        additional_services=["Bar", "Console"],
    )

    assert schema.purpose == "Birthday party"
    assert schema.calendar_id == "wfwafwjag2@goog.com"
    assert schema.guests == 5
    assert schema.event_state == EventState.CONFIRMED
    assert schema.additional_services == ["Bar", "Console"]


def test_event_schema_extends_base():
    """
    Test that Event schema includes all base fields.
    """
    schema = Event(
        id="some_id_string",
        purpose="Birthday party",
        guests=5,
        email="coolEmail@buk.cvut.cz",
        start_datetime="2025-05-12T11:00",
        end_datetime="2025-05-12T16:00",
        event_state=EventState.CONFIRMED,
        user_id=21412,
        calendar_id="wfwafwjag2@goog.com",
        additional_services=["Bar", "Console"],
    )
    assert isinstance(schema, EventInDBBase)
    assert schema.purpose == "Birthday party"


@pytest.mark.parametrize("field", [
    "id",
    "purpose",
    "guests",
    "email",
    "start_datetime",
    "end_datetime",
    "event_state",
    "user_id",
    "calendar_id",
])
def test_event_create_required_fields(field):
    """
    Test that omitting required fields raises validation error.
    """
    data = {
        "id": "some_id_string",
        "purpose": "Birthday party",
        "guests": 5,
        "email": "coolEmail@buk.cvut.cz",
        "start_datetime": "2025-05-12T11:00",
        "end_datetime": "2025-05-12T16:00",
        "event_state": EventState.CONFIRMED,
        "user_id": 21412,
        "calendar_id": "wfwafwjag2@goog.com",
    }
    del data[field]
    with pytest.raises(ValidationError):
        EventCreateToDb(**data)
