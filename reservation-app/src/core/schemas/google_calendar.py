"""DTO schemes for Data from Google Calendar."""

from pydantic import BaseModel, ConfigDict, Field


class ConferenceProperties(BaseModel):
    """Represents the conference capabilities of a Google Calendar."""

    allowed_conference_solution_types: list[str] | None = Field(
        default=None, alias="allowedConferenceSolutionTypes"
    )

    model_config = ConfigDict(populate_by_name=True)


class GoogleCalendarCalendar(BaseModel):
    """Represents a Google Calendar object as returned by the Google Calendar API."""

    kind: str
    etag: str
    id: str
    summary: str | None = None
    description: str | None = None
    location: str | None = None
    time_zone: str | None = Field(default=None, alias="timeZone")
    primary: bool | None = None
    access_role: str | None = Field(default=None, alias="accessRole")
    conference_properties: ConferenceProperties | None = Field(
        default=None, alias="conferenceProperties"
    )

    model_config = ConfigDict(populate_by_name=True)


class EventTime(BaseModel):
    """Represents the start or end time of a Google Calendar event."""

    date_time: str | None = Field(default=None, alias="dateTime")
    time_zone: str | None = Field(default=None, alias="timeZone")


class EventEmail(BaseModel):
    """Represents an attendee's email and response status in a Google Calendar event."""

    email: str
    response_status: str | None = Field(default=None, exclude=True, alias="responseStatus")


class GoogleCalendarEventCreate(BaseModel):
    """Represents the data required to create a new Google Calendar event."""

    summary: str
    description: str
    start: EventTime
    end: EventTime
    attendees: list[EventEmail]

    model_config = {"populate_by_name": True}


class EventCreator(BaseModel):
    """Represents the creator of a Google Calendar event."""

    email: str


class EventOrganizer(BaseModel):
    """Represents the organizer of a Google Calendar event."""

    email: str
    display_name: str | None = Field(default=None, alias="displayName")
    self_: bool | None = Field(default=None, alias="self")


class GoogleCalendarEvent(BaseModel):
    """Represents a full Google Calendar event object."""

    kind: str
    etag: str
    id: str
    status: str
    html_link: str | None = Field(default=None, alias="htmlLink")
    created: str | None = None
    updated: str | None = None
    summary: str | None = None
    description: str | None = None
    creator: EventCreator | None = None
    organizer: EventOrganizer | None = None
    start: EventTime
    end: EventTime
    i_cal_uid: str | None = Field(default=None, alias="iCalUID")
    sequence: int | None = None
    attendees: list[EventEmail] | None = None
    reminders: dict | None = None
    event_type: str | None = Field(default=None, alias="eventType")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
