"""Events enum module."""

from enum import StrEnum


class EventActor(StrEnum):
    """Actor types for event permissions."""

    OWNER = "owner"
    MANAGER = "manager"


class EventState(StrEnum):
    """
    State of the event.

    - **not_approved** - The event has been created but not yet approved.
    - **update_request** - A user has requested changes to the event.
    - **confirmed** - The event is confirmed.
    - **canceled** - The event was previously scheduled but has been canceled.
    """

    NOT_APPROVED = "not_approved"
    UPDATE_REQUESTED = "update_requested"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
