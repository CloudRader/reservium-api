"""
DTO schemes for Event entity.
Test variation
"""
from pydantic import BaseModel
from datetime import datetime


class EventCreate(BaseModel):
    """Schema for creating an event."""
    start_datetime: datetime
    end_datetime: datetime
    purpose: str
    guests: int
    reservation_type: str
    email: str
    additional_services: list[str] | None = None
    username: str
