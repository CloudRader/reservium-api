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
