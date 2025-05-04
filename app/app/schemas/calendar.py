"""DTO schemes for Calendar entity."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


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
    collision_with_calendar: List[str] = Field(default_factory=list)
    more_than_max_people_with_permission: bool | None = None
    mini_services: List[str] = Field(default_factory=list)
    color: str | None = None


class CalendarCreate(CalendarBase):
    """Properties to receive via API on creation."""
    reservation_service_id: UUID
    reservation_type: str
    max_people: int = Field(ge=1)
    collision_with_itself: bool
    club_member_rules: Rules
    active_member_rules: Rules
    manager_rules: Rules


class CalendarUpdate(CalendarBase):
    """Properties to receive via API on update."""
    reservation_type: str | None = None
    max_people: int | None = Field(None, ge=1)
    collision_with_itself: bool | None = None
    collision_with_calendar: List[str] = Field(default_factory=list)
    club_member_rules: Rules | None = None
    active_member_rules: Rules | None = None
    manager_rules: Rules | None = None
    mini_services: List[str] = Field(default_factory=list)


class CalendarInDBBase(CalendarBase):
    """Base model for calendar in database."""
    id: str
    deleted_at: Optional[datetime] = None
    reservation_type: str
    max_people: int
    collision_with_itself: bool
    club_member_rules: Rules
    active_member_rules: Rules
    manager_rules: Rules
    reservation_service_id: UUID

    # pylint: disable=too-few-public-methods
    # reason: Config class only needs to set orm_mode to True.
    class Config:
        """Config class for database calendar model."""
        from_attributes = True


class Calendar(CalendarInDBBase):
    """Additional properties of calendar to return via API."""


class CalendarInDB(CalendarInDBBase):
    """Additional properties stored in DB"""
