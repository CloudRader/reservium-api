"""DTO schemes for ReservationService entity."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from schemas import MiniService, Calendar


class ReservationServiceBase(BaseModel):
    """Shared properties of ReservationService."""
    web: str | None = None
    contact_mail: str | None = None
    public: bool | None = None
    lockers_id: List[int] = Field(default_factory=list)
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


class ReservationServiceInDBBase(ReservationServiceBase):
    """Base model for reservation service in database."""
    id: UUID
    deleted_at: Optional[datetime] = None
    name: str
    alias: str
    calendars: list[Calendar] = Field(default_factory=list)
    mini_services: list[MiniService] = Field(default_factory=list)

    # pylint: disable=too-few-public-methods
    # reason: Config class only needs to set orm_mode to True.
    class Config:
        """Config class for database mini service model."""
        from_attributes = True


class ReservationService(ReservationServiceInDBBase):
    """Additional properties of reservation service to return via API."""


class ReservationServicerInDB(ReservationServiceInDBBase):
    """Additional properties stored in DB"""
