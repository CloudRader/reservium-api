"""DTO schemes for EventExtra entity."""

from datetime import datetime
from typing import Any
from uuid import UUID

from infrastructure.database.sqlalchemy.models.event import EventState
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
                message = "Invalid datetime format"
                raise ValueError(message) from exc
            if parsed.tzinfo is not None:
                message = "Datetime must be naive (no timezone info)"
                raise ValueError(message)
            return parsed  # return datetime object

        if isinstance(value, datetime):
            if value.tzinfo is not None:
                message = "Datetime must be naive (no timezone info)"
                raise ValueError(message)
            return value

        message = "Invalid datetime value"
        raise ValueError(message)

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
    calendar_id: UUID
    email: EmailStr
    additional_services: list[str] = Field(default_factory=list)

    _validate_naive = make_naive_datetime_validator("start_datetime", "end_datetime")

    @model_validator(mode="after")
    def check_time_order(self) -> "EventCreate":  # noqa
        if self.end_datetime <= self.start_datetime:
            message = "End time must be after start time"
            raise ValueError(message)
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

    user_id: UUID | None = None
    calendar_id: UUID | None = None

    _validate_naive = make_naive_datetime_validator(
        "reservation_start",
        "reservation_end",
        "requested_reservation_start",
        "requested_reservation_end",
    )

    @model_validator(mode="after")
    def check_time_order(self) -> "EventUpdate":  # noqa
        if (
            self.reservation_start
            and self.reservation_end
            and self.reservation_end <= self.reservation_start
        ):
            message = "End time must be after start time"
            raise ValueError(message)
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
    def check_time_order(self) -> "EventUpdateTime":  # noqa
        if self.requested_reservation_end <= self.requested_reservation_start:
            message = "End time must be after start time"
            raise ValueError(message)
        return self


class EventLite(EventBase):
    """Base model for event in database."""

    id: UUID | None = None
    reservation_start: datetime
    reservation_end: datetime
    requested_reservation_start: datetime | None = None
    requested_reservation_end: datetime | None = None
    purpose: str
    guests: int
    email: EmailStr
    event_state: EventState

    user_id: UUID
    calendar_id: UUID

    provider_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EventDetail(EventLite):
    """Extend properties of event to return via API."""

    user: "UserLite"  # noqa
    calendar: "CalendarWithReservationServiceInfo"  # noqa


from application.schemas.user import UserLite  # noqa
from application.schemas.calendar import CalendarWithReservationServiceInfo, CalendarLite  # noqa

EventDetail.model_rebuild()
