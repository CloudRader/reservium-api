"""
API router for v1 of the Reservation System.
"""

from fastapi import APIRouter
from api.v1 import (
    auth_router,
    users_router,
    reservation_services_router,
    calendars_router,
    mini_services_router,
    events_router,
    emails_router,
    access_card_system_router,
)

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
