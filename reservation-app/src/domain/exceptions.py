"""Domain exception classes."""

from typing import final


@final
class DomainValidationError(Exception):
    """Exception raised when a domain model invariant is violated."""
