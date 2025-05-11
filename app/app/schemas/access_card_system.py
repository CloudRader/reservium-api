"""
DTO schemes for Access Card System entity.
"""
from pydantic import BaseModel


class VarSymbolCreateUpdate(BaseModel):
    """Schema for creating or updating a var symbol in access card system."""
    var_symbol: int
    group: str
    valid_from: str
    valid_to: str


class VarSymbolDelete(BaseModel):
    """Schema for creating or updating a var symbol in access card system."""
    var_symbol: int
    group: str


class ClubAccessSystemRequest(BaseModel):
    """
    Schema for handling club access card system.
    """
    uid: int
    room_id: int
    device_id: int
