"""DTO schemes for CalendarDetail entity."""

from datetime import datetime

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

    id: str | None = None
    collision_with_calendar: list[str] = Field(default_factory=list)
    more_than_max_people_with_permission: bool | None = None
    color: str | None = None


class CalendarCreate(CalendarBase):
    """Properties to receive via API on creation."""

    reservation_service_id: str
    reservation_type: str
    max_people: int = Field(ge=1)
    collision_with_itself: bool
    club_member_rules: Rules
    active_member_rules: Rules
    manager_rules: Rules
    mini_services: list[str] = Field(default_factory=list)


class CalendarUpdate(CalendarBase):
    """Properties to receive via API on update."""

    reservation_type: str | None = None
    max_people: int | None = Field(None, ge=1)
    collision_with_itself: bool | None = None
    collision_with_calendar: list[str] = Field(default_factory=list)
    club_member_rules: Rules | None = None
    active_member_rules: Rules | None = None
    manager_rules: Rules | None = None
    mini_services: list[str] = Field(default_factory=list)


class CalendarLite(CalendarBase):
    """Base model for calendar in database."""

    id: str
    deleted_at: datetime | None = None
    reservation_type: str
    max_people: int
    collision_with_itself: bool
    reservation_service_id: str

    model_config = ConfigDict(from_attributes=True)


class CalendarWithReservationServiceInfo(CalendarLite):
    """Additional properties of calendar to return via API."""

    reservation_service: "ReservationServiceLite"


class CalendarDetail(CalendarLite):
    """Additional properties of calendar to return via API."""

    club_member_rules: Rules
    active_member_rules: Rules
    manager_rules: Rules
    mini_services: list["MiniServiceLite"] = Field(default_factory=list)


from core.schemas.reservation_service import ReservationServiceLite  # noqa
from core.schemas.mini_service import MiniServiceLite  # noqa

CalendarWithReservationServiceInfo.model_rebuild()
CalendarDetail.model_rebuild()
