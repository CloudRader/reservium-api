"""Base domain entity definition."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseEntity:
    """Base class for all domain entities, containing ID and audit timestamps."""

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
