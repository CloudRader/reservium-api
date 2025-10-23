"""DTO schemes for EventExtra entity."""

from datetime import datetime
from typing import Any

from core.models.event import EventState
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


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

    @model_validator(mode="after")
    def check_time_order(self) -> "EventCreate":
        if self.end_datetime <= self.start_datetime:
            raise ValueError("End time must be after start time")
        return self


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

    @model_validator(mode="after")
    def check_time_order(self) -> "EventUpdate":
        if (
            self.reservation_start
            and self.reservation_end
            and self.reservation_end <= self.reservation_start
        ):
            raise ValueError("End time must be after start time")
        return self


class EventUpdateTime(BaseModel):
    """Properties to receive via API on update reservation time."""

    requested_reservation_start: datetime
    requested_reservation_end: datetime

    _validate_naive = make_naive_datetime_validator(
        "requested_reservation_start",
        "requested_reservation_end",
    )

    @model_validator(mode="after")
    def check_time_order(self) -> "EventUpdateTime":
        if self.requested_reservation_end <= self.requested_reservation_start:
            raise ValueError("End time must be after start time")
        return self


class EventLite(EventBase):
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

    model_config = ConfigDict(from_attributes=True)


class EventDetail(EventLite):
    """Extend properties of event to return via API."""

    user: "UserLite"
    calendar: "CalendarWithReservationServiceInfo"


class EventTimeline(BaseModel):
    """Extend properties of event to return via API."""

    past: list[EventDetail]
    upcoming: list[EventDetail]


from core.schemas.user import UserLite  # noqa
from core.schemas.calendar import CalendarWithReservationServiceInfo, CalendarLite  # noqa

EventDetail.model_rebuild()
