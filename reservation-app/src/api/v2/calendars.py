"""API controllers for calendars."""

import logging
from typing import Annotated, Any

from api import check_create_multiple_permissions, check_create_permissions, get_current_user
from api.api_base import BaseCRUDRouter
from core.application.exceptions import ERROR_RESPONSES, Entity
from core.schemas import CalendarCreate, CalendarDetail, CalendarLite, CalendarUpdate, UserLite
from core.schemas.calendar import CalendarDetailWithCollisions
from fastapi import APIRouter, Depends, Path, Query, status
from integrations.google import GoogleCalendarService
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
            enable_create=False,
            enable_create_multiple=False,
        )

        self.register_routes()

        @router.get(
            "/{id}/mini_services",
            status_code=status.HTTP_200_OK,
            deprecated=True,
        )
        async def get_mini_services_by_calendar(
            service: Annotated[CalendarService, Depends(CalendarService)],
            id_: Annotated[str, Path(alias="id")],
        ) -> Any:
            """
            Get mini services by its calendar (DEPRECATED!!!).

            :param service: CalendarDetail service.
            :param id_: id of the calendar.

            :return: List mini services with type equal to service type
                     or None if no such calendars exists.
            """
            return await service.get_mini_services_by_calendar(id_)

        @router.get(
            "/google/importable",
            responses=ERROR_RESPONSES["401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def google_calendars_available_for_import(
            service: Annotated[CalendarService, Depends(CalendarService)],
            google_calendar_service: Annotated[
                GoogleCalendarService,
                Depends(GoogleCalendarService),
            ],
            user: Annotated[UserLite, Depends(get_current_user)],
        ) -> Any:
            """List Google calendars that the auth user owns but are not yet added to the system."""
            google_calendars = await google_calendar_service.get_all_calendars()

            return await service.google_calendars_available_for_import(user, google_calendars)

        @router.post(
            "/",
            response_model=CalendarDetail,
            responses=ERROR_RESPONSES["400_401_403_409"],
            dependencies=[Depends(check_create_permissions(CalendarService, CalendarCreate))],
            status_code=status.HTTP_201_CREATED,
        )
        async def create(
            service: Annotated[CalendarService, Depends(CalendarService)],
            google_calendar_service: Annotated[
                GoogleCalendarService,
                Depends(GoogleCalendarService),
            ],
            obj_create: CalendarCreate,
        ) -> Any:
            """Create calendar, only users with special roles can create calendar."""
            calendar = await _create_single_object(service, google_calendar_service, obj_create)
            logger.debug("Created calendar: %s", calendar)
            return calendar

        @router.post(
            "/batch",
            response_model=list[CalendarDetail],
            responses=ERROR_RESPONSES["400_401_403_409"],
            dependencies=[Depends(check_create_multiple_permissions(CalendarService))],
            status_code=status.HTTP_201_CREATED,
        )
        async def create_multiple(
            service: Annotated[CalendarService, Depends(CalendarService)],
            google_calendar_service: Annotated[
                GoogleCalendarService,
                Depends(GoogleCalendarService),
            ],
            objs_create: list[CalendarCreate],
        ) -> Any:
            """Create calendars, only users with special roles can create calendar."""
            calendars_result: list[CalendarDetail] = []
            for calendar in objs_create:
                calendar_obj = await _create_single_object(
                    service,
                    google_calendar_service,
                    calendar,
                )
                logger.debug("Created calendar: %s", calendar_obj)
                calendars_result.append(calendar_obj)

            return calendars_result

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

        async def _create_single_object(
            service: CalendarService,
            google_calendar_service: GoogleCalendarService,
            calendar_create: CalendarCreate,
        ) -> Any:
            """
            Help creating a single calendar with permission checks.

            :param service: Service providing business logic of this calendar.
            :param google_calendar_service: Google CalendarDetail service.
            :param calendar_create: CalendarDetail Create schema.

            :return: The created CalendarDetail instance.
            """
            if calendar_create.id:
                await google_calendar_service.user_has_calendar_access(calendar_create.id)
            else:
                calendar_create.id = (
                    await google_calendar_service.create_calendar(
                        calendar_create.reservation_type,
                    )
                ).id

            return await service.create(calendar_create)


CalendarRouter()
