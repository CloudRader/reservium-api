"""API controllers for calendars."""

import logging
from typing import Annotated, Any
from uuid import UUID

from api.api_base import BaseCRUDRouter
from api.dependencies import (
    get_current_user,
)
from api.permissions import abac_manage_rs_by_id, abac_manage_rs_from_body
from application.schemas import (
    CalendarCreate,
    CalendarSchema,
    CalendarUpdate,
    MiniServiceSchema,
    UserSchema,
)
from application.schemas.calendar import CalendarWithCollisions
from application.services import CalendarService, MiniServiceService
from core.bootstrap.exceptions import ERROR_RESPONSES, Entity, PermissionDeniedError
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Path, Query, status
from infrastructure.calendar.google import (
    CalendarImportResult,
    GoogleCalendarCalendar,
    GoogleCalendarImportRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class CalendarRouter(
    BaseCRUDRouter[
        CalendarCreate,
        CalendarUpdate,
        CalendarSchema,
        CalendarService,
    ]
):
    """
    API router for managing Calendars.

    This class extends `BaseCRUDRouter` to automatically register standard
    CRUD routes for the `Calendars` entity and adds custom endpoints
    specific to Calendars.
    """

    def __init__(self):
        super().__init__(
            router=router,
            service_dep=CalendarService,
            schema_create=CalendarCreate,
            schema_update=CalendarUpdate,
            schema_read=CalendarSchema,
            entity_name=Entity.CALENDAR,
            permissions_create=("calendars.create",),
            permissions_update=("calendars.update",),
            permissions_restore=("calendars.restore",),
            permissions_delete=("calendars.soft_delete",),
            permissions_hard_delete=("calendars.hard_delete",),
            abac_create=[abac_manage_rs_from_body(CalendarCreate)],
            abac_update=[abac_manage_rs_by_id()],
            abac_restore=[abac_manage_rs_by_id()],
            abac_delete=[abac_manage_rs_by_id()],
        )

        self.register_routes()

        @router.get(
            "/{id}/mini_services",
            response_model=list[MiniServiceSchema],
            status_code=status.HTTP_200_OK,
        )
        @inject
        async def get_mini_services_by_calendar(
            mini_service_service: FromDishka[MiniServiceService],
            id_: Annotated[UUID, Path(alias="id")],
            include_removed: bool = Query(False, description="Include `removed object` or not."),
        ) -> Any:
            """Get all mini services linked to a calendar."""
            return await mini_service_service.get_by_calendar_id(id_, include_removed)

        @router.get(
            "/google/importable",
            responses=ERROR_RESPONSES["401_403"],
            status_code=status.HTTP_200_OK,
        )
        @inject
        async def google_calendars_available_for_import(
            service: FromDishka[CalendarService],
            user: Annotated[UserSchema, Depends(get_current_user)],
        ) -> Any:
            """List Google calendars that the auth user owns but are not yet added to the system."""
            if not user.roles:
                raise PermissionDeniedError()
            return await service.google_calendars_available_for_import()

        @router.post("/google/subscribe-calendars")
        @inject
        async def google_subscribe_calendars(
            service: FromDishka[CalendarService],
            google_calendar_ids: GoogleCalendarImportRequest,
            user: Annotated[UserSchema, Depends(get_current_user)],
        ) -> list[CalendarImportResult]:
            """Subscribe the service account to specified Google Calendars."""
            if not user.roles:
                raise PermissionDeniedError()
            return await service.google_subscribe_calendars(google_calendar_ids.calendar_ids)

        @router.post("/google/subscribe-existing-calendars")
        @inject
        async def google_subscribe_existing_calendars(
            service: FromDishka[CalendarService],
            user: Annotated[UserSchema, Depends(get_current_user)],
        ) -> list[CalendarImportResult]:
            """Ensure the service account is subscribed to all calendars stored in the system."""
            if not user.roles:
                raise PermissionDeniedError()
            return await service.google_subscribe_existing_calendars()

        @router.get(
            "/google/calendars",
            status_code=status.HTTP_200_OK,
        )
        @inject
        async def get_google_calendars(
            service: FromDishka[CalendarService],
        ) -> list[GoogleCalendarCalendar]:
            """Retrieve all Google Calendars the service account is subscribed to."""
            return await service.google_get_subscribed_calendars()

        @router.get(
            "/{id}/collisions",
            response_model=CalendarWithCollisions,
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        @inject
        async def get_with_collisions(
            service: FromDishka[CalendarService],
            id_: Annotated[UUID, Path(alias="id")],
            include_removed: bool = Query(False, description="Include `removed object` or not."),
        ) -> Any:
            """Get calendar with collisions."""
            logger.info(
                "Fetching calendar with collisions for id=%s (include_removed=%s)",
                id_,
                include_removed,
            )
            calendars = await service.get_with_collisions(id_, include_removed)
            logger.debug("Fetched calendar with collisions: %s", calendars)
            return calendars


CalendarRouter()
