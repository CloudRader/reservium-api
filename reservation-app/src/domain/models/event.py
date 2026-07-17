"""Event domain entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import final
from uuid import UUID

from domain.enums import EventState
from domain.exceptions import DomainValidationError
from domain.models.base import BaseEntity


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class Event(BaseEntity):
    """Domain Entity representing an Event."""

    reservation_start: datetime
    reservation_end: datetime
    purpose: str
    guests: int
    email: str
    user_id: UUID
    calendar_id: UUID
    requested_reservation_start: datetime | None = None
    requested_reservation_end: datetime | None = None
    event_state: EventState = EventState.NOT_APPROVED
    provider_id: str | None = None
    additional_services: list[str] | None = None

    def __post_init__(self) -> None:
        """Validate business invariants of Event."""
        if self.reservation_end <= self.reservation_start:
            message = "Reservation end time must be after start time"
            raise DomainValidationError(message)
        if not self.purpose.strip():
            message = "Purpose cannot be empty"
            raise DomainValidationError(message)
        if self.guests < 0:
            message = "Guests count must be non-negative"
            raise DomainValidationError(message)
        if not self.email.strip():
            message = "Email cannot be empty"
            raise DomainValidationError(message)

        if (
            self.requested_reservation_start is not None
            or self.requested_reservation_end is not None
        ):
            if self.requested_reservation_start is None or self.requested_reservation_end is None:
                message = "Both requested reservation start and end times must be provided together"
                raise DomainValidationError(message)
            if self.requested_reservation_end <= self.requested_reservation_start:
                message = "Requested reservation end time must be after start time"
                raise DomainValidationError(message)
