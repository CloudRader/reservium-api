"""Calendar domain entity."""

from dataclasses import dataclass, field
from typing import final
from uuid import UUID

from domain.entities.base import BaseEntity
from domain.exceptions import DomainValidationError
from domain.value_objects import Rules


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Calendar(BaseEntity):
    """Domain Entity representing a Calendar."""

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
    collision_ids: list[UUID] = field(default_factory=list)
    mini_service_ids: list[UUID] = field(default_factory=list)

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
