"""
DTO schemes for Event entity.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, EmailStr
from models.event import EventState


class EventBase(BaseModel):
    """Shared properties of Event."""
    additional_services: List[str] = Field(default_factory=list)


class EventCreate(BaseModel):
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
    event_state: EventState | None = None

    user_id: int | None = None
    calendar_id: str | None = None


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
