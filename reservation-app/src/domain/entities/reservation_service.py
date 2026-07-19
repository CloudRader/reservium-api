"""ReservationService domain entity."""

from dataclasses import dataclass
from typing import final

from domain.entities.base import BaseEntity
from domain.exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class ReservationService(BaseEntity):
    """Domain Entity representing a Reservation Service."""

    name: str
    alias: str
    contact_mail: str
    public: bool = True
    web: str

    def __post_init__(self) -> None:
        """Validate business invariants of ReservationService."""
        if not self.name.strip():
            message = "Name cannot be empty"
            raise DomainValidationError(message)
        if not self.alias.strip():
            message = "Alias cannot be empty"
            raise DomainValidationError(message)
        if len(self.alias) > 6:
            message = "Alias must be at most 6 characters"
            raise DomainValidationError(message)
        if not self.contact_mail.strip():
            message = "Contact email cannot be empty"
            raise DomainValidationError(message)
