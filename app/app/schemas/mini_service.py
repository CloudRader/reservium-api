"""DTO schemes for MiniService entity."""
from uuid import UUID
from pydantic import BaseModel


class MiniServiceBase(BaseModel):
    """Shared properties of MiniService."""
    name: str | None = None
    service_alias: str | None = None


class MiniServiceCreate(MiniServiceBase):
    """Properties to receive via API on creation."""
    name: str
    service_alias: str


class MiniServiceUpdate(MiniServiceBase):
    """Properties to receive via API on update."""
    name: str | None = None
    service_alias: str | None = None


class MiniServiceInDBBase(MiniServiceBase):
    """Base model for mini service in database."""
    uuid: UUID
    name: str
    service_alias: str

    # pylint: disable=too-few-public-methods
    # reason: Config class only needs to set orm_mode to True.
    class Config:
        """Config class for database mini service model."""
        from_attributes = True


class MiniService(MiniServiceInDBBase):
    """Additional properties of mini service to return via API."""


class MiniServicerInDB(MiniServiceInDBBase):
    """Additional properties stored in DB"""
