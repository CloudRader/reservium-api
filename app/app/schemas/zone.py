"""
DTO schemes for Room entity.
"""
from typing import Optional
from pydantic import BaseModel


class Zone(BaseModel):
    """Represents a zone."""
    alias: Optional[str]
    id: int
    name: str
    note: str


class Room(BaseModel):
    """Represents a room in the IS."""
    door_number: str
    floor: int
    id: int
    name: Optional[str]
    zone: Zone
