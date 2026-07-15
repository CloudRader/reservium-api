"""Calendar domain entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, final
from uuid import UUID

from domain.exceptions import DomainValidationError

if TYPE_CHECKING:
    from .event import Event
    from .mini_service import MiniService


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Rules:
    """Represents booking rules for a member type."""

    night_time: bool
    reservation_without_permission: bool
    max_reservation_hours: int
    in_advance_hours: int
    in_advance_minutes: int
    in_prior_days: int

    def __post_init__(self) -> None:
        """Validate business invariants of Rules."""
        if self.max_reservation_hours < 0:
            message = "Max reservation hours must be non-negative"
            raise DomainValidationError(message)
        if self.in_advance_hours < 0:
            message = "In advance hours must be non-negative"
            raise DomainValidationError(message)
        if self.in_advance_minutes < 0:
            message = "In advance minutes must be non-negative"
            raise DomainValidationError(message)
        if self.in_prior_days < 0:
            message = "In prior days must be non-negative"
            raise DomainValidationError(message)


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Calendar:
    """Domain Entity representing a Calendar."""

    id: UUID
    reservation_type: str
    reservation_service_id: UUID
    color: str = "#05baf5"
    max_people: int = 0
    more_than_max_people_with_permission: bool = True
    collision_with_itself: bool = False
    club_member_rules: Rules | None = None
    active_member_rules: Rules | None = None
    manager_rules: Rules | None = None
    provider_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    collisions: list[Calendar] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    mini_services: list[MiniService] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate business invariants of Calendar."""
        if not self.reservation_type.strip():
            message = "Reservation type cannot be empty"
            raise DomainValidationError(message)
        if self.max_people < 0:
            message = "Max people must be non-negative"
            raise DomainValidationError(message)
        if not self.color.startswith("#") or len(self.color) not in (4, 7):
            message = f"Invalid color format: '{self.color}'"
            raise DomainValidationError(message)

    @property
    def collision_ids(self) -> list[UUID]:
        """Return only the IDs of calendars this one collides with."""
        return [c.id for c in self.collisions if hasattr(c, "id")]
