"""DTO schemes for Calendar entity."""
from uuid import UUID
from pydantic import BaseModel


class Rules(BaseModel):
    """Represents rules of user."""
    night_time: bool
    reservation_without_permission: bool
    max_reservation_hours: int
    in_advance_hours: int
    in_advance_minutes: int
    # How many prior days can a person reserve for
    in_prior_days: int


class CalendarBase(BaseModel):
    """Shared properties of Calendar."""
    collision_with_calendar: list[str] | None = None
    mini_services: list[str] | None = None


class CalendarCreate(CalendarBase):
    """Properties to receive via API on creation."""
    id: str
    reservation_service_uuid: UUID
    reservation_type: str
    max_people: int
    collision_with_itself: bool
    club_member_rules: Rules
    active_member_rules: Rules
    manager_rules: Rules


class CalendarUpdate(CalendarBase):
    """Properties to receive via API on update."""
    reservation_type: str | None = None
    max_people: int | None = None
    collision_with_itself: bool | None = None
    collision_with_calendar: list[str] | None = None
    club_member_rules: Rules | None = None
    active_member_rules: Rules | None = None
    manager_rules: Rules | None = None
    mini_services: list[str] | None = None


class CalendarInDBBase(CalendarBase):
    """Base model for user in database."""
    id: str
    is_active: bool
    reservation_type: str
    max_people: int
    collision_with_itself: bool
    club_member_rules: Rules
    active_member_rules: Rules
    manager_rules: Rules
    reservation_service_uuid: UUID

    # pylint: disable=too-few-public-methods
    # reason: Config class only needs to set orm_mode to True.
    class Config:
        """Config class for database user model."""
        from_attributes = True


class Calendar(CalendarInDBBase):
    """Additional properties of calendar to return via API."""


class CalendarInDB(CalendarInDBBase):
    """Additional properties stored in DB"""
