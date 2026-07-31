"""MiniService domain entity."""

from dataclasses import dataclass
from typing import final
from uuid import UUID

from domain.entities.base import BaseEntity
from domain.exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class MiniService(BaseEntity):
    """Domain Entity representing a MiniService."""

    name: str
    reservation_service_id: UUID

    def __post_init__(self) -> None:
        """Validate business invariants of MiniService."""
        if not self.name.strip():
            message = "Name cannot be empty"
            raise DomainValidationError(message)
