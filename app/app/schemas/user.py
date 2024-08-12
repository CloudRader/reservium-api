"""
DTO schemes for User entity.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    """Shared properties of User."""
    roles: list[str] | None = None


class UserCreate(UserBase):
    """Properties to receive via API on creation."""
    id: int
    username: str
    active_member: bool
    section_head: bool


class UserUpdate(UserBase):
    """Properties to receive via API on update."""
    username: str | None = None
    active_member: bool | None = None
    section_head: bool | None = None


class UserInDBBase(UserBase):
    """Base model for user in database."""
    id: int
    deleted_at: Optional[datetime] = None
    username: str
    active_member: bool
    section_head: bool

    # pylint: disable=too-few-public-methods
    # reason: Config class only needs to set orm_mode to True.
    class Config:
        """Config class for database user model."""
        from_attributes = True


class User(UserInDBBase):
    """Additional properties of user to return via API."""


class UserInDB(UserInDBBase):
    """Additional properties stored in DB"""
