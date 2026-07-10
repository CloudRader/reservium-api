"""Google-specific service integrations such as Calendar and Authentication."""

from infrastructure.calendar.google.provider import GoogleCalendarProvider
from infrastructure.calendar.google.schemas import (
    CalendarImportResult,
    ConferenceProperties,
    EventCreator,
    EventEmail,
    EventOrganizer,
    EventTime,
    GoogleCalendarCalendar,
    GoogleCalendarEvent,
    GoogleCalendarEventCreate,
    GoogleCalendarImportRequest,
)

__all__ = [
    "CalendarImportResult",
    "ConferenceProperties",
    "EventCreator",
    "EventEmail",
    "EventOrganizer",
    "EventTime",
    "GoogleCalendarCalendar",
    "GoogleCalendarEvent",
    "GoogleCalendarEventCreate",
    "GoogleCalendarImportRequest",
    "GoogleCalendarProvider",
]
