"""User domain entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, final
from uuid import UUID

from domain.exceptions import DomainValidationError

if TYPE_CHECKING:
    from .event import Event


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class User:
    """Domain Entity representing a User."""

    id: UUID
    username: str
    full_name: str
    provider_id: str
    active_member: bool = False
    roles: list[str] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    events: list[Event] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate business invariants of User."""
        if not self.username.strip():
            message = "Username cannot be empty"
            raise DomainValidationError(message)
        if not self.full_name.strip():
            message = "Full name cannot be empty"
            raise DomainValidationError(message)
        if not self.provider_id.strip():
            message = "Provider ID cannot be empty"
            raise DomainValidationError(message)
