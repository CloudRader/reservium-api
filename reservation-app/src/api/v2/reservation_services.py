"""API controllers for reservation services."""

from typing import Annotated, Any

from api.api_base import BaseCRUDRouter
from core.application.exceptions import (
    ERROR_RESPONSES,
    Entity,
)
from core.models.event import EventState
from core.schemas import (
    Calendar,
    MiniService,
    ReservationService,
    ReservationServiceCreate,
    ReservationServiceUpdate,
)
from core.schemas.event import EventDetailLite
from fastapi import APIRouter, Depends, Path, Query, status
from services import ReservationServiceService

router = APIRouter()


class ReservationServiceRouter(
    BaseCRUDRouter[
        ReservationServiceCreate,
        ReservationServiceUpdate,
        ReservationService,
        ReservationServiceService,
    ]
):
    """
    API router for managing Reservation Services.

    This class extends `BaseCRUDRouter` to automatically register standard
    CRUD routes for the `ReservationService` entity and adds custom endpoints
    specific to Reservation Services.
    """

    def __init__(self):
        super().__init__(
            router=router,
            service_dep=ReservationServiceService,
            schema_create=ReservationServiceCreate,
            schema_update=ReservationServiceUpdate,
            schema=ReservationService,
            entity_name=Entity.RESERVATION_SERVICE,
        )

        @router.get(
            "/public",
            response_model=list[ReservationService],
            status_code=status.HTTP_200_OK,
        )
        async def get_public(
            service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
        ) -> Any:
            """
            Get all public reservation services from database.

            :param service: Reservation Service ser.

            :return: List of all public reservation services or None if
            there are no reservation services in db.
            """
            return await service.get_public_services()

        self.register_routes()

        @router.get(
            "/name/{name}",
            response_model=ReservationService,
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_by_name(
            service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
            name: Annotated[str, Path()],
            include_removed: bool = Query(False),
        ) -> Any:
            """
            Get reservation services by its name.

            :param service: Mini Service ser.
            :param name: service alias of the mini service.
            :param include_removed: include removed reservation service or not.

            :return: Reservation Service with name equal to name
                     or None if no such reservation service exists.
            """
            reservation_service = await service.get_by_name(name, include_removed)
            return await self._handle_not_found(reservation_service, name)

        @router.get(
            "/alias/{alias}",
            response_model=ReservationService,
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_by_alias(
            service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
            alias: Annotated[str, Path()],
            include_removed: bool = Query(False),
        ) -> Any:
            """
            Get reservation services by its alias.

            :param service: Mini Service ser.
            :param alias: service alias of the mini service.
            :param include_removed: include removed reservation service or not.

            :return: Reservation Service with alias equal to alias
                     or None if no such reservation service exists.
            """
            reservation_service = await service.get_by_alias(alias, include_removed)
            return await self._handle_not_found(reservation_service, alias)

        @router.get(
            "/{alias}/calendars",
            response_model=list[Calendar],
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_calendars_by_reservation_service(
            service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
            alias: Annotated[str, Path()],
            include_removed: bool = Query(False),
        ) -> Any:
            """
            Get all calendars linked to a reservation service by its ID.

            :param service: Reservation Service ser.
            :param alias: alias of the reservation service.
            :param include_removed: include removed calendars or not.

            :return: List of Calendar objects linked to the reservation service.
            """
            return await service.get_calendars_by_alias(alias, include_removed)

        @router.get(
            "/{alias}/mini-services",
            response_model=list[MiniService],
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_mini_services_by_reservation_service(
            service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
            alias: Annotated[str, Path()],
            include_removed: bool = Query(False),
        ) -> Any:
            """
            Get all mini services linked to a reservation service by its ID.

            :param service: Reservation Service ser.
            :param alias: alias of the reservation service.
            :param include_removed: include removed calendars or not.

            :return: List of MiniService objects linked to the reservation service.
            """
            return await service.get_mini_services_by_alias(alias, include_removed)

        @router.get(
            "/{alias}/events",
            response_model=list[EventDetailLite],
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_events_by_reservation_service(
            service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
            alias: Annotated[str, Path()],
            event_state: Annotated[EventState | None, Query()] = None,
        ) -> Any:
            """
            Get all events linked to a reservation service by its alias.

            :param service: Event service.
            :param alias: alias of the reservation service.
            :param event_state: event state of the event.

            :return: List of Event objects linked to the reservation service.
            """
            return await service.get_events_by_alias(alias, event_state)


ReservationServiceRouter()
