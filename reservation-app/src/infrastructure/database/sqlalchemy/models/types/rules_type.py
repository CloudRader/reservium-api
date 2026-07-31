"""Custom SQLAlchemy type for storing Pydantic models as JSON in TEXT columns."""

import dataclasses
from typing import Any

from domain.value_objects import Rules as DomainRules
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator


class RulesType(TypeDecorator):
    """SQLAlchemy TypeDecorator mapping PostgreSQL JSON/JSONB to Domain Rules dataclass."""

    impl = JSONB
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> dict[str, Any] | None:  # noqa: ARG002
        """Before saving to DB: convert Domain Rules dataclass -> dict for SQL JSON."""
        if value is None:
            return None
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            return dataclasses.asdict(value)
        if isinstance(value, dict):
            return value
        message = f"Expected Rules dataclass instance or dict, got {type(value)}"
        raise TypeError(message)

    def process_result_value(self, value: Any, dialect: Any) -> DomainRules | None:  # noqa: ARG002
        """After reading from DB: convert dict -> Domain Rules dataclass."""
        if value is None:
            return None
        if isinstance(value, dict):
            return DomainRules(**value)
        message = f"Expected dict or DomainRules from DB, got {type(value)}"
        raise TypeError(message)
