"""DTO schemes for Event entity."""

from datetime import datetime
from typing import Any

from core.models.event import EventState
from pydantic import BaseModel, EmailStr, Field, field_validator


def make_naive_datetime_validator(*fields: str):
    """Create a naive datetime validator for given field names."""

    @field_validator(*fields, mode="before")
    def _check_naive_datetime(cls, value: Any) -> Any:  # noqa: ARG001
        if value is None:
            return value

        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError("Invalid datetime format") from exc
            if parsed.tzinfo is not None:
                raise ValueError("Datetime must be naive (no timezone info)")
            return parsed  # return datetime object

        if isinstance(value, datetime):
            if value.tzinfo is not None:
                raise ValueError("Datetime must be naive (no timezone info)")
            return value

        raise ValueError("Invalid datetime value")

    return _check_naive_datetime


class EventBase(BaseModel):
    """Shared properties of Event."""

    additional_services: list[str] = Field(default_factory=list)


class EventCreate(BaseModel):
    """Schema for creating an event from the reservation form."""

    start_datetime: datetime
    end_datetime: datetime
    purpose: str = Field(max_length=40)
    guests: int = Field(ge=1)
    calendar_id: str
    email: EmailStr
    additional_services: list[str] = Field(default_factory=list)

    _validate_naive = make_naive_datetime_validator("start_datetime", "end_datetime")


class EventUpdate(EventBase):
    """Properties to receive via API on update."""

    purpose: str | None = None
    guests: int | None = None
    reservation_start: datetime | None = None
    reservation_end: datetime | None = None
    requested_reservation_start: datetime | None = None
    requested_reservation_end: datetime | None = None
    email: EmailStr | None = None
    event_state: EventState | None = None

    user_id: int | None = None
    calendar_id: str | None = None

    _validate_naive = make_naive_datetime_validator(
        "reservation_start",
        "reservation_end",
        "requested_reservation_start",
        "requested_reservation_end",
    )


class EventUpdateTime(BaseModel):
    """Properties to receive via API on update reservation time."""

    requested_reservation_start: datetime | None = None
    requested_reservation_end: datetime | None = None

    _validate_naive = make_naive_datetime_validator(
        "requested_reservation_start",
        "requested_reservation_end",
    )


class EventInDBBase(EventBase):
    """Base model for event in database."""

    id: str
    reservation_start: datetime
    reservation_end: datetime
    requested_reservation_start: datetime | None = None
    requested_reservation_end: datetime | None = None
    purpose: str
    guests: int
    email: EmailStr
    event_state: EventState

    user_id: int
    calendar_id: str

    class Config:
        """Config class for database event model."""

        from_attributes = True


class Event(EventInDBBase):
    """Additional properties of event to return via API."""


class EventDetailLite(Event):
    """Extend properties of event to return via API."""

    user: "User"
    calendar: "CalendarBase"


class EventDetail(Event):
    """Extend properties of event to return via API."""

    user: "User"
    calendar: "CalendarWithReservationServiceInfoLite"


class EventWithCalendarInfo(Event):
    """Extend properties of event to return via API."""

    calendar: "CalendarWithReservationServiceInfoLite"


class EventInDB(EventInDBBase):
    """Additional properties stored in DB."""


from core.schemas.user import User  # noqa
from core.schemas.calendar import CalendarWithReservationServiceInfoLite, CalendarBase  # noqa

EventDetail.model_rebuild()
EventDetailLite.model_rebuild()
EventWithCalendarInfo.model_rebuild()
