"""API controllers for calendars."""

from typing import Annotated, Any

from api import get_current_user
from api.api_base import BaseCRUDRouter
from core.application.exceptions import ERROR_RESPONSES, BaseAppError, Entity
from core.schemas import CalendarCreate, CalendarDetail, CalendarLite, CalendarUpdate, UserLite
from fastapi import APIRouter, Depends, Path, status
from integrations.google import GoogleCalendarService
from services import CalendarService

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
            "/{calendar_id}/mini_services",
            status_code=status.HTTP_200_OK,
            deprecated=True,
        )
        async def get_mini_services_by_calendar(
            service: Annotated[CalendarService, Depends(CalendarService)],
            calendar_id: Annotated[str, Path()],
        ) -> Any:
            """
            Get mini services by its calendar (DEPRECATED!!!).

            :param service: CalendarDetail service.
            :param calendar_id: id of the calendar.

            :return: List mini services with type equal to service type
                     or None if no such calendars exists.
            """
            return await service.get_mini_services_by_calendar(calendar_id)

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
            """
            List Google calendars that the auth user owns but are not yet added to the system.

            This includes all non-primary calendars where the user has 'owner' access and
            that are not already stored in the local database.

            :param service: CalendarDetail service.
            :param google_calendar_service: Google CalendarDetail service.
            :param user: UserLite who make this request.

            :returns: List of importable Google CalendarDetail entries.
            """
            google_calendars = await google_calendar_service.get_all_calendars()

            return await service.google_calendars_available_for_import(user, google_calendars)

        @router.post(
            "/",
            response_model=CalendarDetail,
            responses=ERROR_RESPONSES["400_401_403_404"],
            status_code=status.HTTP_201_CREATED,
        )
        async def create(
            service: Annotated[CalendarService, Depends(CalendarService)],
            google_calendar_service: Annotated[
                GoogleCalendarService,
                Depends(GoogleCalendarService),
            ],
            user: Annotated[UserLite, Depends(get_current_user)],
            calendar_create: CalendarCreate,
        ) -> Any:
            """
            Create calendar, only users with special roles can create calendar.

            :param service: CalendarDetail service.
            :param google_calendar_service: Google CalendarDetail service.
            :param user: UserLite who make this request.
            :param calendar_create: CalendarDetail Create schema.

            :returns CalendarModel: the created calendar.
            """
            return await _create_single_object(
                service, google_calendar_service, user, calendar_create
            )

        @router.post(
            "/batch",
            response_model=list[CalendarDetail],
            responses=ERROR_RESPONSES["400_401_403_404"],
            status_code=status.HTTP_201_CREATED,
        )
        async def create_multiple(
            service: Annotated[CalendarService, Depends(CalendarService)],
            google_calendar_service: Annotated[
                GoogleCalendarService,
                Depends(GoogleCalendarService),
            ],
            user: Annotated[UserLite, Depends(get_current_user)],
            calendars_create: list[CalendarCreate],
        ) -> Any:
            """
            Create calendars, only users with special roles can create calendar.

            :param service: CalendarDetail service.
            :param google_calendar_service: Google CalendarDetail service.
            :param user: UserLite who make this request.
            :param calendars_create: Calendars Create schema.

            :returns CalendarModel: the created calendar.
            """
            calendars_result: list[CalendarDetail] = []
            for calendar in calendars_create:
                calendars_result.append(
                    await _create_single_object(service, google_calendar_service, user, calendar),
                )

            return calendars_result

        async def _create_single_object(
            service: CalendarService,
            google_calendar_service: GoogleCalendarService,
            user: UserLite,
            calendar_create: CalendarCreate,
        ) -> Any:
            """
            Help creating a single calendar with permission checks.

            :param service: Service providing business logic of this calendar.
            :param google_calendar_service: Google CalendarDetail service.
            :param user: Authenticated user performing the creation.
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

            calendar = await service.create_with_permission_checks(calendar_create, user)
            if not calendar:
                raise BaseAppError()
            return calendar


CalendarRouter()
