"""DTO schemes for MiniServiceDetail entity."""

from datetime import datetime

from core.schemas.calendar import CalendarLite
from pydantic import BaseModel, ConfigDict, Field


class MiniServiceBase(BaseModel):
    """Shared properties of MiniService."""

    lockers_id: list[int] = Field(default_factory=list)
    access_group: str | None = None
    room_id: int | None = None


class MiniServiceCreate(MiniServiceBase):
    """Properties to receive via API on creation."""

    reservation_service_id: str
    name: str


class MiniServiceUpdate(MiniServiceBase):
    """Properties to receive via API on update."""

    name: str | None = None


class MiniServiceLite(MiniServiceBase):
    """Base model for mini service in database."""

    id: str
    deleted_at: datetime | None = None
    name: str
    reservation_service_id: str

    model_config = ConfigDict(from_attributes=True)


class MiniServiceDetail(MiniServiceLite):
    """Additional properties of mini service to return via API."""

    calendars: list[CalendarLite] = Field(default_factory=list)
