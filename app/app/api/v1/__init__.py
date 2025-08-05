"""API router for v1 of the Reservation System."""

from api.docs import fastapi_docs
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
    tags=[fastapi_docs.AUTHORISATION_TAG["name"]],
)

router.include_router(
    users_router,
    prefix="/users",
    tags=[fastapi_docs.USER_TAG["name"]],
)

router.include_router(
    reservation_services_router,
    prefix="/reservation-services",
    tags=[fastapi_docs.RESERVATION_SERVICE_TAG["name"]],
)

router.include_router(
    calendars_router,
    prefix="/calendars",
    tags=[fastapi_docs.CALENDAR_TAG["name"]],
)

router.include_router(
    mini_services_router,
    prefix="/mini-services",
    tags=[fastapi_docs.MINI_SERVICE_TAG["name"]],
)

router.include_router(
    events_router,
    prefix="/events",
    tags=[fastapi_docs.EVENT_TAG["name"]],
)

router.include_router(
    emails_router,
    prefix="/emails",
    tags=[fastapi_docs.EMAIL_TAG["name"]],
)

router.include_router(
    access_card_system_router,
    prefix="/cards",
    tags=[fastapi_docs.ACCESS_CARD_SYSTEM_TAG["name"]],
)
