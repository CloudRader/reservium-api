"""Events enum module."""

from enum import StrEnum


class EventActor(StrEnum):
    """Actor types for event permissions."""

    OWNER = "owner"
    MANAGER = "manager"
