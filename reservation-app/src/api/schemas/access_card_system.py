"""DTO schemes for Access Card System entity."""

from pydantic import BaseModel


class ClubAccessSystemRequest(BaseModel):
    """Schema for handling club access card system."""

    uid: int
    room_id: int
    device_id: int
