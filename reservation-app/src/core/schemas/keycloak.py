"""DTO schemes for Data from Keycloak."""

from pydantic import BaseModel


class UserKeycloak(BaseModel):
    """Represent a user in the Keycloak."""

    sub: str
    ldap_id: int
    preferred_username: str
    name: str
    given_name: str
    family_name: str
    email: str
    email_verified: bool
    roles: list[str]
    services: list[str]
    tags: str
