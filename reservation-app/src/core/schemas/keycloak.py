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


class CurrentUser(BaseModel):
    """Represent the current user."""

    id: str = Field(alias="sub")
    username: str = Field(alias="preferred_username")
    email: EmailStr

    roles: list[str] = Field(default_factory=list)
    resource_roles: list[str] = Field(default_factory=list)
    groups: list[str] = Field(default_factory=list)

    @classmethod
    def from_token(cls, token: dict, client_id: str) -> CurrentUser:
        return cls(
            sub=token["sub"],
            preferred_username=token["preferred_username"],
            email=token["email"],
            roles=token.get("roles", []),
            resource_roles=(token.get("resource_access", {}).get(client_id, {}).get("roles", [])),
            groups=token.get("groups", []),
        )

    def has_permission(self, permission: str) -> bool:
        return permission in self.resource_roles
