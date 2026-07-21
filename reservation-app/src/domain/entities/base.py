"""Base domain entity definition."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from common import get_utc_now


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseEntity:
    """Base class for all domain entities, containing ID and audit timestamps."""

    id: UUID = field(default_factory=uuid7)
    created_at: datetime = field(default_factory=get_utc_now)
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
