"""DTO schemes for MiniService entity."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MiniServiceBase(BaseModel):
    """Shared properties of MiniService."""

    lockers_id: list[int] = Field(default_factory=list)
    access_group: str | None = None
    room_id: int | None = None


class MiniServiceCreate(MiniServiceBase):
    """Properties to receive via API on creation."""

    reservation_service_id: UUID
    name: str


class MiniServiceUpdate(MiniServiceBase):
    """Properties to receive via API on update."""

    name: str | None = None


class MiniServiceInDBBase(MiniServiceBase):
    """Base model for mini service in database."""

    id: UUID
    deleted_at: datetime | None = None
    name: str
    reservation_service_id: UUID

    class Config:
        """Config class for database mini service model."""

        from_attributes = True


class MiniService(MiniServiceInDBBase):
    """Additional properties of mini service to return via API."""


class MiniServicerInDB(MiniServiceInDBBase):
    """Additional properties stored in DB."""
