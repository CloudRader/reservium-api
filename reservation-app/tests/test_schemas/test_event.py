"""Tests for MiniServiceDetail Pydantic Schemas."""

from datetime import datetime, timezone

import pytest
from core.models import EventState
from core.schemas.calendar import CalendarWithReservationServiceInfo
from core.schemas.event import (
    EventBase,
    EventCreate,
    EventDetail,
    EventLite,
    EventUpdate,
    EventUpdateTime,
    make_naive_datetime_validator,
)
from core.schemas.reservation_service import ReservationServiceLite
from core.schemas.user import UserLite
from pydantic import ValidationError

# ----------------------------------------------------------------------
# make_naive_datetime_validator tests
# ----------------------------------------------------------------------


def test_make_naive_datetime_validator_accepts_naive_datetime():
    """Ensure the validator accepts naive datetime objects."""
    validator = make_naive_datetime_validator("start")
    dt = datetime(2025, 1, 1, 12, 0)
    assert validator.__wrapped__(None, dt) == dt


def test_make_naive_datetime_validator_rejects_aware_datetime():
    """Ensure validator rejects timezone-aware datetime values."""
    validator = make_naive_datetime_validator("start")
    aware_dt = datetime(2025, 1, 1, 12, 0).astimezone()
    with pytest.raises(ValueError, match="Datetime must be naive"):
        validator.__wrapped__(None, aware_dt)


def test_make_naive_datetime_validator_parses_valid_string():
    """Test validator correctly parses valid ISO-format datetime strings."""
    validator = make_naive_datetime_validator("start")
    result = validator.__wrapped__(None, "2025-01-01T12:00")
    assert isinstance(result, datetime)
    assert result.tzinfo is None


def test_make_naive_datetime_validator_invalid_string():
    """Ensure validator raises an error for invalid datetime strings."""
    validator = make_naive_datetime_validator("start")
    with pytest.raises(ValueError, match="Invalid datetime format"):
        validator.__wrapped__(None, "invalid-date")


def test_make_naive_datetime_validator_invalid_type():
    """Ensure validator rejects invalid types (non-datetime, non-string)."""
    validator = make_naive_datetime_validator("start")
    with pytest.raises(ValueError, match="Invalid datetime value"):
        validator.__wrapped__(None, 12345)


def test_check_naive_datetime_accepts_none():
    """Validator should accept None."""
    validator = make_naive_datetime_validator("start")
    assert validator.__wrapped__(None, None) is None


def test_check_naive_datetime_rejects_tzaware_string():
    """Validator should reject timezone-aware datetime strings."""
    validator = make_naive_datetime_validator("start")
    aware_str = "2025-01-01T12:00+01:00"
    with pytest.raises(ValueError, match="Datetime must be naive"):
        validator.__wrapped__(None, aware_str)


# ----------------------------------------------------------------------
# EventCreate tests
# ----------------------------------------------------------------------


def test_event_create_valid():
    """Test creating an event with valid data."""
    schema = EventLite(
        id="some_id_string",
        purpose="Birthday party",
        guests=5,
        email="coolEmail@buk.cvut.cz",
        reservation_start=datetime.fromisoformat("2025-05-12T11:00"),
        reservation_end=datetime.fromisoformat("2025-05-12T16:00"),
        event_state=EventState.CONFIRMED,
        user_id=21412,
        calendar_id="wfwafwjag2@goog.com",
    )
    assert schema.purpose == "Birthday party"
    assert schema.calendar_id == "wfwafwjag2@goog.com"
    assert schema.guests == 5
    assert schema.event_state == EventState.CONFIRMED
    assert schema.user_id == 21412


def test_event_create_validates_order():
    """Ensure EventCreate accepts valid datetime order."""
    start = datetime(2025, 5, 12, 10)
    end = datetime(2025, 5, 12, 11)
    schema = EventCreate(
        start_datetime=start,
        end_datetime=end,
        purpose="Meeting",
        guests=10,
        calendar_id="abc@calendar.com",
        email="user@example.com",
    )
    assert schema.purpose == "Meeting"
    assert schema.guests == 10


def test_event_create_rejects_end_before_start():
    """Ensure EventCreate rejects end times before start times."""
    start = datetime(2025, 5, 12, 11)
    end = datetime(2025, 5, 12, 10)
    with pytest.raises(ValidationError, match="End time must be after start time"):
        EventCreate(
            start_datetime=start,
            end_datetime=end,
            purpose="Bad event",
            guests=5,
            calendar_id="id@calendar.com",
            email="user@example.com",
        )


def test_event_create_rejects_tzaware_start():
    """Ensure EventCreate rejects timezone-aware datetimes."""
    start = datetime(2025, 5, 12, 11).astimezone()
    end = datetime(2025, 5, 12, 12)
    with pytest.raises(ValidationError):
        EventCreate(
            start_datetime=start,
            end_datetime=end,
            purpose="Test",
            guests=3,
            calendar_id="c@id.com",
            email="x@y.com",
        )


# ----------------------------------------------------------------------
# EventUpdate tests
# ----------------------------------------------------------------------


def test_event_update_partial():
    """Test updating event with partial data."""
    update = EventUpdate(purpose="New Purpose")
    assert update.purpose == "New Purpose"


def test_event_update_valid_and_invalid_order():
    """Validate that EventUpdate enforces correct datetime order."""
    valid = EventUpdate(
        reservation_start=datetime(2025, 1, 1, 10),
        reservation_end=datetime(2025, 1, 1, 12),
    )
    assert valid.reservation_end > valid.reservation_start

    # invalid (end before start)
    with pytest.raises(ValidationError, match="End time must be after start time"):
        EventUpdate(
            reservation_start=datetime(2025, 1, 1, 12),
            reservation_end=datetime(2025, 1, 1, 11),
        )


# ----------------------------------------------------------------------
# EventUpdateTime tests
# ----------------------------------------------------------------------


def test_event_update_time_valid():
    """Ensure EventUpdateTime accepts valid times."""
    start = datetime(2025, 1, 1, 10)
    end = datetime(2025, 1, 1, 11)
    schema = EventUpdateTime(
        requested_reservation_start=start,
        requested_reservation_end=end,
    )
    assert schema.requested_reservation_end > schema.requested_reservation_start


def test_event_update_time_invalid():
    """Ensure EventUpdateTime rejects invalid time ordering."""
    start = datetime(2025, 1, 1, 12)
    end = datetime(2025, 1, 1, 11)
    with pytest.raises(ValidationError, match="End time must be after start time"):
        EventUpdateTime(
            requested_reservation_start=start,
            requested_reservation_end=end,
        )


def test_event_in_db_base_schema():
    """Test full event DB representation."""
    schema = EventLite(
        id="some_id_string",
        purpose="Birthday party",
        guests=5,
        email="coolEmail@buk.cvut.cz",
        reservation_start=datetime.fromisoformat("2025-05-12T11:00"),
        reservation_end=datetime.fromisoformat("2025-05-12T16:00"),
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
    """Test that EventExtra schema includes all base fields."""
    schema = EventLite(
        id="some_id_string",
        purpose="Birthday party",
        guests=5,
        email="coolEmail@buk.cvut.cz",
        reservation_start=datetime.fromisoformat("2025-05-12T11:00"),
        reservation_end=datetime.fromisoformat("2025-05-12T16:00"),
        event_state=EventState.CONFIRMED,
        user_id=21412,
        calendar_id="wfwafwjag2@goog.com",
        additional_services=["Bar", "Console"],
    )
    assert isinstance(schema, EventBase)
    assert schema.purpose == "Birthday party"


@pytest.mark.parametrize(
    "field",
    [
        "id",
        "purpose",
        "guests",
        "email",
        "start_datetime",
        "end_datetime",
        "event_state",
        "user_id",
        "calendar_id",
    ],
)
def test_event_create_required_fields(field):
    """Test that omitting required fields raises validation error."""
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
        EventDetail(**data)


def test_event_detail_includes_nested_models():
    """Ensure EventDetail correctly includes nested user and calendar objects."""
    service = ReservationServiceLite(
        id="r212414", name="Dorm Booking", email="service@uni.cz", alias="club"
    )

    calendar = CalendarWithReservationServiceInfo(
        id="cal-999",
        reservation_type="Main Hall",
        max_people=200,
        collision_with_itself=False,
        reservation_service_id=service.id,
        reservation_service=service,
    )

    user = UserLite(
        id=999,
        username="fakeuser",
        full_name="Fake User",
        active_member=True,
        section_head=False,
    )

    schema = EventDetail(
        id="event123",
        purpose="Workshop",
        guests=10,
        email="user@example.com",
        reservation_start=datetime(2025, 5, 12, 10, 0, tzinfo=timezone.utc),
        reservation_end=datetime(2025, 5, 12, 12, 0, tzinfo=timezone.utc),
        event_state=EventState.CONFIRMED,
        user_id=1,
        calendar_id="cal123",
        user=user,
        calendar=calendar,
    )

    assert schema.user.full_name == "Fake User"
    assert schema.calendar.id == "cal-999"
    assert isinstance(schema.user, UserLite)
    assert isinstance(schema.calendar, CalendarWithReservationServiceInfo)
