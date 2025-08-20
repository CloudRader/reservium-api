"""DTO schemes for Data from IS."""

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Represent token response from IS."""

    access_token: str
    expires_in: int
    scope: str
    token_type: str


class Organization(BaseModel):
    """Represent an organization."""

    name: str | None
    note: str | None


class UserIS(BaseModel):
    """Represent a user in the IS."""

    country: str
    created_at: str
    email: str
    first_name: str
    id: int
    im: str | None
    note: str | None
    organization: Organization | None
    phone: str | None
    phone_vpn: str | None
    photo_file: str | None
    photo_file_small: str | None
    state: str
    surname: str
    ui_language: str | None
    ui_skin: str
    username: str
    usertype: str


class Service(BaseModel):
    """Represent a service."""

    alias: str
    name: str
    note: str | None
    servicetype: str
    web: str


class ServiceValidity(BaseModel):
    """Represent a service validity."""

    from_: str | None = Field(None, alias="from")
    to: str | None
    note: str | None
    service: Service
    usetype: str


class ServiceList(BaseModel):
    """Represent a list user services."""

    services: list[ServiceValidity]


class LimitObject(BaseModel):
    """Represent a limit object."""

    id: int
    name: str
    alias: str | None = None
    note: str | None = None
    # description: Optional[str]


class Role(BaseModel):
    """Represent a role."""

    role: str
    name: str
    description: str
    limit: str
    limit_objects: list[LimitObject]


class RoleList(BaseModel):
    """Represent a list user roles."""

    roles: list[Role]


class Zone(BaseModel):
    """Represent a zone."""

    alias: str | None
    id: int
    name: str
    note: str


class Room(BaseModel):
    """Represent a room in the IS."""

    door_number: str
    floor: int
    id: int
    name: str | None
    zone: Zone


class InformationFromIS(BaseModel):
    """Represent all information about user from IS."""

    user: UserIS
    room: Room
    services: list[ServiceValidity]
