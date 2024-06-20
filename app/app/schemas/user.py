"""
DTO schemes for User entity.
"""
from uuid import UUID
from pydantic import BaseModel


class UserBase(BaseModel):
    """Shared properties of User."""
    username: str | None = None
    user_token: str | None = None
    active_member: bool | None = None
    roles: list[str] | None = None


class UserCreate(UserBase):
    """Properties to receive via API on creation."""
    username: str
    user_token: str
    active_member: bool


class UserUpdate(UserBase):
    """Properties to receive via API on update."""
    user_token: str | None = None
    active_member: bool | None = None


class UserInDBBase(UserBase):
    """Base model for user in database."""
    uuid: UUID
    username: str
    user_token: str
    active_member: bool
    roles: list[str]

    # pylint: disable=too-few-public-methods
    # reason: Config class only needs to set orm_mode to True.
    class Config:
        """Config class for database user model."""
        from_attributes = True


class User(UserInDBBase):
    """Additional properties of user to return via API."""


class UserInDB(UserInDBBase):
    """Additional properties stored in DB"""
