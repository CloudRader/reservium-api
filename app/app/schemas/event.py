"""
DTO schemes for Event entity.
Test variation
"""
from pydantic import BaseModel


class EventInput(BaseModel):
    start_datetime: str
    end_datetime: str
    purpose: str
    guests: int
    reservation_type: str