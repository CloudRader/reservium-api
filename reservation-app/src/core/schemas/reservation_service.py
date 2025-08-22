"""DTO schemes for ReservationServiceDetail entity."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReservationServiceBase(BaseModel):
    """Shared properties of ReservationService."""

    web: str | None = None
    contact_mail: str | None = None
    public: bool | None = None
    lockers_id: list[int] = Field(default_factory=list)
    access_group: str | None = None
    room_id: int | None = None


class ReservationServiceCreate(ReservationServiceBase):
    """Properties to receive via API on creation."""

    name: str
    alias: str = Field(max_length=6)


class ReservationServiceUpdate(ReservationServiceBase):
    """Properties to receive via API on update."""

    name: str | None = None
    alias: str | None = Field(None, max_length=6)


class ReservationServiceLite(ReservationServiceBase):
    """Base model for reservation service in database."""

    id: str
    deleted_at: datetime | None = None
    name: str
    alias: str

    model_config = ConfigDict(from_attributes=True)


class ReservationServiceDetail(ReservationServiceLite):
    """Additional properties of reservation service to return via API."""

    calendars: list["CalendarDetail"] = Field(default_factory=list)
    mini_services: list["MiniServiceLite"] = Field(default_factory=list)


from core.schemas.calendar import CalendarDetail  # noqa
from core.schemas.mini_service import MiniServiceLite  # noqa

ReservationServiceLite.model_rebuild()
