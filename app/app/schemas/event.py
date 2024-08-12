"""
DTO schemes for Event entity.
Test variation
"""
from datetime import datetime
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    """Schema for creating an event."""
    start_datetime: datetime
    end_datetime: datetime
    purpose: str
    guests: int = Field(ge=1)
    reservation_type: str
    email: str
    additional_services: list[str] | None = None
