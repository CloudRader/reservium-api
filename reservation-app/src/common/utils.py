"""Utils for common functions used across the application."""

import re
from datetime import UTC, datetime


def snake_case(name: str) -> str:
    """
    Convert a camelCase or PascalCase string to snake_case.

    :param name: The string to convert.
    :return: The converted string in snake_case.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def get_utc_now() -> datetime:
    """Get the current UTC time."""
    return datetime.now(UTC)
