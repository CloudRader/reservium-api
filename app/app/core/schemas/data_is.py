"""
DTO schemes for Data from IS.
"""


from pydantic import BaseModel, Field


class Organization(BaseModel):
    """Represents an organization."""

    name: str | None
    note: str | None


class UserIS(BaseModel):
    """Represents a user in the IS."""

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
    """Represents a service."""

    alias: str
    name: str
    note: str | None
    servicetype: str
    web: str


class ServiceValidity(BaseModel):
    """Represents a service validity."""

    from_: str | None = Field(None, alias="from")
    to: str | None
    note: str | None
    service: Service
    usetype: str


class ServiceList(BaseModel):
    """Represents a list user services."""

    services: list[ServiceValidity]


class LimitObject(BaseModel):
    """Represents a limit object."""

    id: int
    name: str
    alias: str | None = None
    note: str | None = None
    # description: Optional[str]


class Role(BaseModel):
    """Represents a role."""

    role: str
    name: str
    description: str
    limit: str
    limit_objects: list[LimitObject]


class RoleList(BaseModel):
    """Represents a list user roles."""

    roles: list[Role]


class Zone(BaseModel):
    """Represents a zone."""

    alias: str | None
    id: int
    name: str
    note: str


class Room(BaseModel):
    """Represents a room in the IS."""

    door_number: str
    floor: int
    id: int
    name: str | None
    zone: Zone


class InformationFromIS(BaseModel):
    """Represents all information about user from IS."""

    user: UserIS
    room: Room
    services: list[ServiceValidity]
