"""Rules domain value object."""

from dataclasses import dataclass
from typing import final

from domain.exceptions import DomainValidationError


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
