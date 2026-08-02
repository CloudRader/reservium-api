"""DTO schemes for ReservationServiceDetail entity."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReservationServiceBase(BaseModel):
    """Shared properties of ReservationService."""

    web: str
    public: bool = Field(default=False)


class ReservationServiceCreate(ReservationServiceBase):
    """Properties to receive via API on creation."""

    name: str
    alias: str = Field(max_length=6)
    contact_mail: str


class ReservationServiceUpdate(BaseModel):
    """Properties to receive via API on update."""

    web: str | None = None
    public: bool | None = None
    name: str | None = None
    alias: str | None = Field(default=None, max_length=6)
    contact_mail: str | None = None


class ReservationServiceSchema(ReservationServiceBase):
    """Base model for reservation service in database."""

    id: UUID | None = None
    deleted_at: datetime | None = None
    name: str
    alias: str
    contact_mail: str

    model_config = ConfigDict(from_attributes=True)


class ReservationServiceWithCalendarsAndMiniServices(ReservationServiceSchema):
    """Additional properties of reservation service to return via API."""

    calendars: list["CalendarSchema"] = Field(default_factory=list)  # noqa
    mini_services: list["MiniServiceSchema"] = Field(default_factory=list)  # noqa


from application.schemas.calendar import CalendarSchema  # noqa
from application.schemas.mini_service import MiniServiceSchema  # noqa

ReservationServiceSchema.model_rebuild()
