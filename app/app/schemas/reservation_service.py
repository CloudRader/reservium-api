"""DTO schemes for ReservationService entity."""
from uuid import UUID
from pydantic import BaseModel


class ReservationServiceBase(BaseModel):
    """Shared properties of ReservationService."""
    web: str | None = None
    contact_mail: str | None = None


class ReservationServiceCreate(ReservationServiceBase):
    """Properties to receive via API on creation."""
    name: str
    alias: str


class ReservationServiceUpdate(ReservationServiceBase):
    """Properties to receive via API on update."""
    name: str | None = None
    alias: str | None = None


class ReservationServiceInDBBase(ReservationServiceBase):
    """Base model for reservation service in database."""
    uuid: UUID
    name: str
    alias: str

    # pylint: disable=too-few-public-methods
    # reason: Config class only needs to set orm_mode to True.
    class Config:
        """Config class for database mini service model."""
        from_attributes = True


class ReservationService(ReservationServiceInDBBase):
    """Additional properties of reservation service to return via API."""


class ReservationServicerInDB(ReservationServiceInDBBase):
    """Additional properties stored in DB"""
