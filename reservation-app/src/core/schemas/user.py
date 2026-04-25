"""DTO schemes for UserLite entity."""

from datetime import datetime

from core.schemas.event import EventDetail
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Shared properties of UserLite."""

    roles: list[str] = Field(default_factory=list)


class UserCreate(UserBase):
    """Properties to receive via API on creation."""

    id: int
    username: str
    full_name: str
    active_member: bool


class UserUpdate(UserBase):
    """Properties to receive via API on update."""

    username: str | None = None
    full_name: str | None = None
    active_member: bool | None = None


class UserLite(UserBase):
    """Base model for user in database."""

    id: int
    deleted_at: datetime | None = None
    username: str
    full_name: str
    active_member: bool

    model_config = ConfigDict(from_attributes=True)


class UserDetail(UserLite):
    """Extended API response schema with events."""

    events: list[EventDetail] = Field(default_factory=list)
