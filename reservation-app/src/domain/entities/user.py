"""User domain entity."""

from dataclasses import dataclass, field
from typing import final

from domain.entities.base import BaseEntity
from domain.exceptions import DomainValidationError


@final
@dataclass(frozen=True, slots=True, kw_only=True)
class User(BaseEntity):
    """Domain Entity representing a User."""

    username: str
    full_name: str
    provider_id: str
    active_member: bool = False
    roles: list[str] = field(default_factory=list)

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
