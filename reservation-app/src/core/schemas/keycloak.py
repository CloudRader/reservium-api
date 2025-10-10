"""DTO schemes for Data from Keycloak."""

from pydantic import BaseModel, EmailStr, Field


class UserKeycloak(BaseModel):
    """Represent a user in the Keycloak."""

    sub: str
    ldap_id: int
    preferred_username: str
    name: str
    given_name: str
    family_name: str
    email: EmailStr
    email_verified: bool
    roles: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
