"""Utilities for permission checking."""

from core.application.exceptions import Entity

PERMISSION_MAP = {
    Entity.RESERVATION_SERVICE: {
        "create": "owner",
        "manage": "admin",
        "delete": "admin",
        "hard_remove": "owner",
    },
    Entity.CALENDAR: {
        "create": "admin",
        "manage": "manage",
        "delete": "manage",
        "hard_remove": "owner",
    },
    Entity.MINI_SERVICE: {
        "create": "admin",
        "manage": "manage",
        "delete": "manage",
        "hard_remove": "owner",
    },
}
