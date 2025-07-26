"""
API router for v1 of the Reservation System.
"""

from api.v1.access_card_system import router as access_card_system_router
from api.v1.auth import router as auth_router
from api.v1.calendars import router as calendars_router
from api.v1.emails import router as emails_router
from api.v1.events import router as events_router
from api.v1.mini_services import router as mini_services_router
from api.v1.reservation_services import router as reservation_services_router
from api.v1.users import router as users_router
from fastapi import APIRouter

router = APIRouter(
    prefix="/v1",
)

router.include_router(
    auth_router,
    prefix="/auth",
)

router.include_router(
    users_router,
    prefix="/users",
)

router.include_router(
    reservation_services_router,
    prefix="/reservation_services",
)

router.include_router(
    calendars_router,
    prefix="/calendars",
)

router.include_router(
    mini_services_router,
    prefix="/mini_services",
)

router.include_router(
    events_router,
    prefix="/events",
)

router.include_router(
    emails_router,
    prefix="/emails",
)

router.include_router(
    access_card_system_router,
    prefix="/access_card_system",
)
