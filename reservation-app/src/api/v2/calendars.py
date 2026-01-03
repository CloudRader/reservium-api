"""API controllers for calendars."""

import logging
from typing import Annotated, Any

from api import get_current_user
from api.api_base import BaseCRUDRouter
from core.application.exceptions import ERROR_RESPONSES, Entity
from core.schemas import (
    CalendarCreate,
    CalendarDetail,
    CalendarLite,
    CalendarUpdate,
    MiniServiceLite,
    UserLite,
)
from core.schemas.calendar import CalendarDetailWithCollisions
from fastapi import APIRouter, Depends, Path, Query, status
from services import CalendarService

logger = logging.getLogger(__name__)

router = APIRouter()


class CalendarRouter(
    BaseCRUDRouter[
        CalendarCreate,
        CalendarUpdate,
        CalendarLite,
        CalendarDetail,
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
            schema_lite=CalendarLite,
            schema_detail=CalendarDetail,
            entity_name=Entity.CALENDAR,
        )

        self.register_routes()

        @router.get(
            "/{id}/mini_services",
            response_model=list[MiniServiceLite],
            status_code=status.HTTP_200_OK,
        )
        async def get_mini_services_by_calendar(
            service: Annotated[CalendarService, Depends(CalendarService)],
            id_: Annotated[str, Path(alias="id")],
        ) -> Any:
            """
            Get all mini services linked to a calendar.

            :param service: CalendarDetail service.
            :param id_: id of the calendar.

            :return: List mini services with type equal to service type
                     or None if no such calendars exists.
            """
            return await service.get_mini_services_by_id(id_)

        @router.get(
            "/google/importable",
            responses=ERROR_RESPONSES["401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def google_calendars_available_for_import(
            service: Annotated[CalendarService, Depends(CalendarService)],
            user: Annotated[UserLite, Depends(get_current_user)],
        ) -> Any:
            """List Google calendars that the auth user owns but are not yet added to the system."""
            return await service.google_calendars_available_for_import(user)

        @router.get(
            "/{id}/collisions",
            response_model=CalendarDetailWithCollisions,
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_with_collisions(
            service: Annotated[CalendarService, Depends(CalendarService)],
            id_: Annotated[str, Path(alias="id")],
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
