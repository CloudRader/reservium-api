"""DTO schemes for MiniService."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MiniServiceBase(BaseModel):
    """Shared properties of MiniService."""


class MiniServiceCreate(MiniServiceBase):
    """Properties to receive via API on creation."""

    reservation_service_id: UUID
    name: str


class MiniServiceUpdate(MiniServiceBase):
    """Properties to receive via API on update."""

    name: str | None = None


class MiniServiceSchema(MiniServiceBase):
    """Base model for mini service in database."""

    id: UUID | None = None
    deleted_at: datetime | None = None
    name: str
    reservation_service_id: UUID

    model_config = ConfigDict(from_attributes=True)
