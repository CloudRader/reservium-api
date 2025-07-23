"""
Package for API modules v1.
"""

from api.v1.auth import router as auth_router
from api.v1.users import router as users_router
from api.v1.reservation_services import router as reservation_services_router
from api.v1.calendars import router as calendars_router
from api.v1.mini_services import router as mini_services_router
from api.v1.events import router as events_router
from api.v1.emails import router as emails_router
from api.v1.access_card_system import router as access_card_system_router


__all__ = [
    "auth_router",
    "users_router",
    "reservation_services_router",
    "calendars_router",
    "mini_services_router",
    "events_router",
    "emails_router",
    "access_card_system_router",
]
