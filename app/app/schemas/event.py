"""
DTO schemes for Event entity.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class EventCreate(BaseModel):
    """Schema for creating an event."""
    start_datetime: datetime
    end_datetime: datetime
    purpose: str = Field(max_length=40)
    guests: int = Field(ge=1)
    reservation_type: str
    email: EmailStr
    additional_services: List[str] = Field(default_factory=list)


class RegistrationFormCreate(BaseModel):
    """Schema for creating a registration form."""
    event_name: str = Field(max_length=40)
    guests: int = Field(ge=1)
    event_start: datetime
    event_end: datetime
    email: EmailStr
    organizers: str
    space: str
    other_space: List[str]
    manager_contact_mail: EmailStr
