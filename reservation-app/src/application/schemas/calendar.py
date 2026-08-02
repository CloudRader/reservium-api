"""DTO schemes for CalendarDetail entity."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Rules(BaseModel):
    """Represents rules of user."""

    night_time: bool
    reservation_without_permission: bool
    max_reservation_hours: int = Field(ge=0)
    in_advance_hours: int = Field(ge=0)
    in_advance_minutes: int = Field(ge=0)
    # How many prior days can a person reserve for
    in_prior_days: int = Field(ge=0)


class CalendarBase(BaseModel):
    """Shared properties of Calendar."""

    more_than_max_people_with_permission: bool = Field(default=True)
    color: str


class CalendarCreate(CalendarBase):
    """Properties to receive via API on creation."""

    reservation_service_id: UUID
    reservation_type: str
    max_people: int = Field(ge=1)
    collision_with_itself: bool
    club_member_rules: Rules
    active_member_rules: Rules
    manager_rules: Rules

    collision_ids: list[UUID] = Field(default_factory=list)
    mini_services: list[UUID] = Field(default_factory=list)

    provider_id: str | None = None


class CalendarUpdate(BaseModel):
    """Properties to receive via API on update."""

    provider_id: str | None = None
    reservation_type: str | None = None
    more_than_max_people_with_permission: bool | None = None
    color: str | None = None
    max_people: int | None = Field(default=None, ge=1)
    collision_with_itself: bool | None = None
    club_member_rules: Rules | None = None
    active_member_rules: Rules | None = None
    manager_rules: Rules | None = None

    collision_ids: list[UUID] = Field(default_factory=list)
    mini_services: list[UUID] = Field(default_factory=list)


class CalendarSchema(CalendarBase):
    """Base model for calendar in database."""

    id: UUID | None = None
    deleted_at: datetime | None = None
    reservation_type: str
    max_people: int
    collision_with_itself: bool
    reservation_service_id: UUID
    club_member_rules: Rules
    active_member_rules: Rules
    manager_rules: Rules

    provider_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CalendarWithReservationServiceInfo(CalendarSchema):
    """Additional properties of calendar to return via API."""

    reservation_service: "ReservationServiceSchema"  # noqa


class CalendarWithMiniServices(CalendarSchema):
    """Additional properties of calendar to return via API."""

    mini_services: list["MiniServiceSchema"] = Field(default_factory=list)  # noqa


class CalendarWithCollisions(CalendarWithMiniServices):
    """Additional properties of calendar to return via API."""

    collision_ids: list[UUID] = Field(default_factory=list)


from application.schemas.reservation_service import ReservationServiceSchema  # noqa
from application.schemas.mini_service import MiniServiceSchema  # noqa

CalendarWithReservationServiceInfo.model_rebuild()
CalendarWithMiniServices.model_rebuild()
