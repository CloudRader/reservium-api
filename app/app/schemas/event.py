"""
DTO schemes for Event entity.
"""
from datetime import datetime
from typing import List, Any
from pydantic import BaseModel, Field, EmailStr, field_validator
from models.event import EventState


# pylint: disable=too-few-public-methods
# reason: This class need for proper validation
class NaiveDatetimeValidatorMixin:
    """
    Mixin to validate that datetime fields are naive (i.e., without timezone info).
    """

    @field_validator("start_datetime", "end_datetime", mode="before")
    def check_naive_datetime(cls, value: Any) -> Any:  # pylint: disable=no-self-argument
        """
        Validates that datetime values are naive (not timezone-aware).

        :param value: Input value (string or datetime)
        :return: Validated value if naive
        :raises ValueError: If datetime is timezone-aware or invalid format
        """
        if value is None:
            return value

        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError("Invalid datetime format") from exc

            if parsed.tzinfo is not None:
                raise ValueError("Datetime must be naive (no timezone info)")
            return value

        if isinstance(value, datetime):
            if value.tzinfo is not None:
                raise ValueError("Datetime must be naive (no timezone info)")
            return value

        raise ValueError("Invalid datetime value")


class EventBase(BaseModel):
    """Shared properties of Event."""
    additional_services: List[str] = Field(default_factory=list)


class EventCreate(NaiveDatetimeValidatorMixin, BaseModel):
    """Schema for creating an event from the reservation form."""
    start_datetime: datetime
    end_datetime: datetime
    purpose: str = Field(max_length=40)
    guests: int = Field(ge=1)
    reservation_type: str
    email: EmailStr
    additional_services: List[str] = Field(default_factory=list)


class EventCreateToDb(EventBase):
    """Properties to receive via API on creation."""
    id: str
    start_datetime: datetime
    end_datetime: datetime
    purpose: str = Field(max_length=40)
    guests: int = Field(ge=1)
    email: EmailStr
    event_state: EventState

    user_id: int
    calendar_id: str


class EventUpdate(EventBase):
    """Properties to receive via API on update."""
    purpose: str | None = None
    guests: int | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    email: EmailStr | None = None
    event_state: EventState | None = None

    user_id: int | None = None
    calendar_id: str | None = None


class EventUpdateTime(NaiveDatetimeValidatorMixin, BaseModel):
    """Properties to receive via API on update reservation time."""
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None


class EventInDBBase(EventBase):
    """Base model for event in database."""
    id: str
    purpose: str
    guests: int
    email: EmailStr
    start_datetime: datetime
    end_datetime: datetime
    event_state: EventState

    user_id: int
    calendar_id: str

    # pylint: disable=too-few-public-methods
    # reason: Config class only needs to set orm_mode to True.
    class Config:
        """Config class for database event model."""
        from_attributes = True


class Event(EventInDBBase):
    """Additional properties of event to return via API."""


class EventInDB(EventInDBBase):
    """Additional properties stored in DB"""


class EventWithExtraDetails(BaseModel):
    """Extend properties of event to return via API."""
    event: Event
    reservation_type: str | None = None
    user_name: str | None = None
    reservation_service_name: str | None = None
