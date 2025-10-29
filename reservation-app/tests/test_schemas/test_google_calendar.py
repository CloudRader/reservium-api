"""Tests for Google Calendar Pydantic Schemas."""

from core.schemas.google_calendar import (
    ConferenceProperties,
    EventCreator,
    EventEmail,
    EventOrganizer,
    EventTime,
    GoogleCalendarCalendar,
    GoogleCalendarEvent,
    GoogleCalendarEventCreate,
)

# ----------------------------------------------------------------------
# ConferenceProperties tests
# ----------------------------------------------------------------------


def test_conference_properties_alias():
    """Test that alias works correctly for allowed_conference_solution_types."""
    data = {"allowedConferenceSolutionTypes": ["hangoutsMeet", "zoom"]}
    conf = ConferenceProperties(**data)
    assert conf.allowed_conference_solution_types == ["hangoutsMeet", "zoom"]
    # Should also accept direct field name
    conf2 = ConferenceProperties(allowed_conference_solution_types=["teams"])
    assert conf2.allowed_conference_solution_types == ["teams"]


# ----------------------------------------------------------------------
# GoogleCalendarCalendar tests
# ----------------------------------------------------------------------


def test_google_calendar_calendar_full():
    """Test full instantiation with aliases."""
    data = {
        "kind": "calendar#calendar",
        "etag": "abc123",
        "id": "cal_1",
        "summary": "My Calendar",
        "timeZone": "UTC",
        "conferenceProperties": {"allowedConferenceSolutionTypes": ["hangoutsMeet"]},
    }
    cal = GoogleCalendarCalendar(**data)
    assert cal.kind == "calendar#calendar"
    assert cal.time_zone == "UTC"
    assert isinstance(cal.conference_properties, ConferenceProperties)
    assert cal.conference_properties.allowed_conference_solution_types == ["hangoutsMeet"]


# ----------------------------------------------------------------------
# EventTime tests
# ----------------------------------------------------------------------


def test_event_time_alias():
    """Test EventTime instantiation with alias."""
    et = EventTime(dateTime="2025-01-01T12:00:00Z", timeZone="UTC")
    assert et.date_time == "2025-01-01T12:00:00Z"
    assert et.time_zone == "UTC"


# ----------------------------------------------------------------------
# EventEmail tests
# ----------------------------------------------------------------------


def test_event_email_alias_and_exclude():
    """Test EventEmail instantiation with alias and optional field."""
    email = EventEmail(email="user@example.com", responseStatus="accepted")
    assert email.email == "user@example.com"
    assert email.response_status == "accepted"


# ----------------------------------------------------------------------
# GoogleCalendarEventCreate tests
# ----------------------------------------------------------------------


def test_google_calendar_event_create():
    """Test GoogleCalendarEventCreate instantiation."""
    create = GoogleCalendarEventCreate(
        summary="Meeting",
        description="Project meeting",
        start=EventTime(dateTime="2025-01-01T10:00:00Z"),
        end=EventTime(dateTime="2025-01-01T11:00:00Z"),
        attendees=[EventEmail(email="user@example.com")],
    )
    assert create.summary == "Meeting"
    assert isinstance(create.start, EventTime)
    assert len(create.attendees) == 1
    assert create.attendees[0].email == "user@example.com"


# ----------------------------------------------------------------------
# GoogleCalendarEvent tests
# ----------------------------------------------------------------------


def test_google_calendar_event_full():
    """Test full GoogleCalendarEvent instantiation with nested models."""
    event = GoogleCalendarEvent(
        kind="calendar#event",
        etag="etag123",
        id="event_1",
        status="confirmed",
        start=EventTime(dateTime="2025-01-01T10:00:00Z"),
        end=EventTime(dateTime="2025-01-01T11:00:00Z"),
        creator=EventCreator(email="creator@example.com"),
        organizer=EventOrganizer(email="org@example.com"),
        attendees=[EventEmail(email="user@example.com")],
    )
    assert event.kind == "calendar#event"
    assert isinstance(event.start, EventTime)
    assert isinstance(event.creator, EventCreator)
    assert len(event.attendees) == 1
