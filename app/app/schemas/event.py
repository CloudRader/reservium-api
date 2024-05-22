"""
DTO schemes for Event entity.
Test variation
"""
from pydantic import BaseModel


class EventCreate(BaseModel):
    """Schema for creating an event."""
    start_datetime: str
    end_datetime: str
    purpose: str
    guests: int
    reservation_type: str
    email: str
    additional_services: list[str] | None = None
    username: str
