"""DTO schemes for Calendar entity."""
from pydantic import BaseModel


class Rules(BaseModel):
    """Represents rules of user."""
    night_time: bool
    reservation_more_24_hours: bool
    in_advance_hours: int
    in_advance_minutes: int
    in_advance_day: int


class CalendarBase(BaseModel):
    """Shared properties of Calendar."""
    collision_with_itself: bool | None = None
    collision_with_calendar: list[str] | None = None
    club_member_rules: Rules | None = None
    active_member_rules: Rules | None = None
    manager_rules: Rules | None = None
    mini_services: list[str] | None = None


class CalendarCreate(CalendarBase):
    """Properties to receive via API on creation."""
    calendar_id: str
    service_alias: str
    reservation_type: str
    event_name: str
    max_people: int
    collision_with_itself: bool
    club_member_rules: Rules
    active_member_rules: Rules
    manager_rules: Rules


class CalendarUpdate(CalendarBase):
    """Properties to receive via API on update."""
    service_alias: str | None = None
    reservation_type: str | None = None
    event_name: str | None = None
    max_people: int | None = None
    collision_with_itself: bool | None = None
    collision_with_calendar: list[str] | None = None
    club_member_rules: Rules | None = None
    active_member_rules: Rules | None = None
    manager_rules: Rules | None = None
    mini_services: list[str] | None = None


class CalendarInDBBase(CalendarBase):
    """Base model for user in database."""
    calendar_id: str
    service_alias: str
    reservation_type: str
    event_name: str
    max_people: int

    # pylint: disable=too-few-public-methods
    # reason: Config class only needs to set orm_mode to True.
    class Config:
        """Config class for database user model."""
        from_attributes = True


class Calendar(CalendarInDBBase):
    """Additional properties of calendar to return via API."""


class CalendarInDB(CalendarInDBBase):
    """Additional properties stored in DB"""
