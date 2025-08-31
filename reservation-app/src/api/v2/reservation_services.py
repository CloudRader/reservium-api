"""API controllers for reservation services."""

from typing import Annotated, Any

from api.api_base import BaseCRUDRouter
from core.application.exceptions import (
    ERROR_RESPONSES,
    Entity,
)
from core.models.event import EventState
from core.schemas import (
    CalendarDetail,
    MiniServiceDetail,
    ReservationServiceCreate,
    ReservationServiceDetail,
    ReservationServiceUpdate,
)
from core.schemas.event import EventDetail
from fastapi import APIRouter, Depends, Path, Query, status
from services import ReservationServiceService

router = APIRouter()


class ReservationServiceRouter(
    BaseCRUDRouter[
        ReservationServiceCreate,
        ReservationServiceUpdate,
        ReservationServiceDetail,
        ReservationServiceDetail,
        ReservationServiceService,
    ]
):
    """
    API router for managing Reservation Services.

    This class extends `BaseCRUDRouter` to automatically register standard
    CRUD routes for the `ReservationServices` entity and adds custom endpoints
    specific to Reservation Services.
    """

    def __init__(self):
        super().__init__(
            router=router,
            service_dep=ReservationServiceService,
            schema_create=ReservationServiceCreate,
            schema_update=ReservationServiceUpdate,
            schema_lite=ReservationServiceDetail,
            schema_detail=ReservationServiceDetail,
            entity_name=Entity.RESERVATION_SERVICE,
        )

        @router.get(
            "/public",
            response_model=list[ReservationServiceDetail],
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
            response_model=ReservationServiceDetail,
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
            response_model=ReservationServiceDetail,
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
            "/{id}/calendars",
            response_model=list[CalendarDetail],
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_calendars_by_reservation_service(
            service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
            id_: Annotated[str, Path(alias="id")],
            include_removed: bool = Query(False),
        ) -> Any:
            """
            Get all calendars linked to a reservation service by its ID.

            :param service: Reservation Service ser.
            :param id_: id of the reservation service.
            :param include_removed: include removed calendars or not.

            :return: List of CalendarDetail objects linked to the reservation service.
            """
            return await service.get_calendars_by_id(id_, include_removed)

        @router.get(
            "/{id}/mini-services",
            response_model=list[MiniServiceDetail],
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_mini_services_by_reservation_service(
            service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
            id_: Annotated[str, Path(alias="id")],
            include_removed: bool = Query(False),
        ) -> Any:
            """
            Get all mini services linked to a reservation service by its ID.

            :param service: Reservation Service ser.
            :param id_: id of the reservation service.
            :param include_removed: include removed calendars or not.

            :return: List of MiniServiceDetail objects linked to the reservation service.
            """
            return await service.get_mini_services_by_id(id_, include_removed)

        @router.get(
            "/{id}/events",
            response_model=list[EventDetail],
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_events_by_reservation_service(
            service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
            id_: Annotated[str, Path(alias="id")],
            event_state: Annotated[EventState | None, Query()] = None,
        ) -> Any:
            """
            Get all events linked to a reservation service by its alias.

            :param service: EventExtra service.
            :param id_: id of the reservation service.
            :param event_state: event state of the event.

            :return: List of EventExtra objects linked to the reservation service.
            """
            return await service.get_events_by_id(id_, event_state)


ReservationServiceRouter()
