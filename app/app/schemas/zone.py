"""
DTO schemes for Zone entity.
Test variation
"""
from typing import Optional
from pydantic import BaseModel


class Zone(BaseModel):
    alias: Optional[str]
    id: int
    name: str
    note: str


class Room(BaseModel):
    door_number: str
    floor: int
    id: int
    name: Optional[str]
    zone: Zone
