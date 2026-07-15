"""MiniService domain entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, final
from uuid import UUID

from domain.exceptions import DomainValidationError

if TYPE_CHECKING:
    from .calendar import Calendar
    from .reservation_service import ReservationService


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MiniService:
    """Domain Entity representing a MiniService."""

    id: UUID
    name: str
    reservation_service_id: UUID
    access_group: str | None = None
    room_id: int | None = None
    lockers_id: list[int] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    reservation_service: ReservationService | None = None
    calendars: list[Calendar] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate business invariants of MiniService."""
        if not self.name.strip():
            message = "Name cannot be empty"
            raise DomainValidationError(message)
