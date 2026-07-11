"""DTO schemes for Data from OpenID Providers."""

from pydantic import BaseModel, EmailStr, Field


class UserInfo(BaseModel):
    """Represent a user in the OpenID Provider."""

    sub: str
    preferred_username: str
    name: str
    given_name: str
    family_name: str
    email: EmailStr
    email_verified: bool
    roles: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
