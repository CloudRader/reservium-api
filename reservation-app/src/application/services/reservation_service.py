"""
Define an abstract base class AbstractMiniServiceService.

This class works with Mini Service.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from api.schemas import (
    CalendarDetail,
    MiniServiceDetail,
    ReservationServiceCreate,
    ReservationServiceDetail,
    ReservationServiceUpdate,
)
from api.schemas.event import EventDetail
from application.interfaces.repositories import ReservationServiceRepository
from application.services import CrudServiceBase
from core.bootstrap.exceptions import (
    Entity,
    EntityNotFoundError,
)
from domain.models import CalendarModel, EventState, MiniServiceModel


class AbstractReservationServiceService(
    CrudServiceBase[
        ReservationServiceDetail,
        ReservationServiceDetail,
        ReservationServiceRepository,
        ReservationServiceCreate,
        ReservationServiceUpdate,
    ],
    ABC,
):
    """
    Abstract class defines the interface for a reservation service ser.

    Provides CRUD operations for a specific ReservationServiceModel.
    """

    @abstractmethod
    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        """
        Retrieve a Reservation Service instance by its alias.

        :param alias: The alias of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Services instance.
        """

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        """
        Retrieve a Reservation Service instance by its name.

        :param name: The name of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance.
        """

    @abstractmethod
    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        """
        Retrieve a Reservation Service instance by its room id.

        :param room_id: The room id of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance.
        """

    @abstractmethod
    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationServiceDetail]:
        """
        Retrieve a public Reservation Service instance.

        :param include_removed: Include removed object or not.

        :return: The public Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_all_services_include_all_removed(
        self,
    ) -> list[ReservationServiceDetail]:
        """
        Retrieve Reservation Services instance include soft removed.

        :return: The Reservation Services instance include
        soft removed if found, None otherwise.
        """

    @abstractmethod
    async def get_calendars_by_id(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> list[CalendarDetail]:
        """
        Retrieve all calendars linked to a given Reservation Service.

        :param id_: The id of the Reservation Service.
        :param include_removed: Include removed calendars or not.

        :return: List of CalendarDetail objects linked to the reservation service.
        """

    @abstractmethod
    async def get_mini_services_by_id(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> list[MiniServiceDetail]:
        """
        Retrieve all mini services linked to a given Reservation Service.

        :param id_: The id of the Reservation Service.
        :param include_removed: Include removed calendars or not.

        :return: List of MiniServiceDetail objects linked to the reservation service.
        """

    @abstractmethod
    async def get_events_by_id(
        self,
        id_: UUID,
        event_state: EventState | None = None,
    ) -> list[EventDetail]:
        """
        Retrieve all events linked to a given Reservation Service.

        :param id_: The id of the Reservation Service.
        :param event_state: event state of the event.

        :return: List of EventWithExtraDetails objects linked to the reservation service.
        """

    @abstractmethod
    async def get_reservation_service(
        self,
        id_: UUID,
    ) -> ReservationServiceDetail:
        """
        Retrieve the reservation service.

        Need for unify method in api base.

        :param id_: The id of the Reservation Service.

        :return: Reservation Service of this mini service if found.
        """


class ReservationServiceService(AbstractReservationServiceService):
    """Class MiniServiceService represent service that work with Mini Service."""

    def __init__(
        self,
        reservation_service_repository: ReservationServiceRepository,
    ):
        super().__init__(reservation_service_repository, Entity.RESERVATION_SERVICE)

    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        reservation_service = await self.repo.get_by_alias(alias, include_removed)
        if reservation_service is None:
            raise EntityNotFoundError(self.entity_name, alias)
        return reservation_service

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        reservation_service = await self.repo.get_by_name(name, include_removed)
        if reservation_service is None:
            raise EntityNotFoundError(self.entity_name, name)
        return reservation_service

    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        reservation_service = await self.repo.get_by_room_id(room_id, include_removed)
        if reservation_service is None:
            raise EntityNotFoundError(self.entity_name, room_id)
        return reservation_service

    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationServiceDetail]:
        services = await self.repo.get_public_services(include_removed)

        return [ReservationServiceDetail.model_validate(service) for service in services]

    async def get_all_services_include_all_removed(
        self,
    ) -> list[ReservationServiceDetail]:
        reservation_services = await self.repo.get_all(True)

        reservation_services_result: list[ReservationServiceDetail] = []

        for reservation_service in reservation_services:
            calendars = await self.repo.get_related_entities_by_reservation_service_id(
                CalendarModel,
                reservation_service.id,
                include_removed=True,
            )

            mini_services = await self.repo.get_related_entities_by_reservation_service_id(
                MiniServiceModel,
                reservation_service.id,
                include_removed=True,
            )

            reservation_service.calendars = calendars
            reservation_service.mini_services = mini_services

            reservation_services_result.append(
                ReservationServiceDetail.model_validate(reservation_service)
            )

        return reservation_services_result

    async def get_calendars_by_id(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> list[CalendarDetail]:
        reservation_service = await self.get(id_, include_removed=True)

        return await self.repo.get_related_entities_by_reservation_service_id(
            CalendarModel, reservation_service.id, include_removed=include_removed
        )

    async def get_mini_services_by_id(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> list[MiniServiceDetail]:
        reservation_service = await self.get(id_, include_removed=True)

        return await self.repo.get_related_entities_by_reservation_service_id(
            MiniServiceModel, reservation_service.id, include_removed=include_removed
        )

    async def get_events_by_id(
        self,
        id_: UUID,
        event_state: EventState | None = None,
    ) -> list[EventDetail]:
        reservation_service = await self.get(id_, include_removed=True)

        events = await self.repo.get_events_by_reservation_service_id(
            reservation_service.id,
            event_state,
        )

        return [EventDetail.model_validate(event) for event in events]

    async def get_reservation_service(
        self,
        id_: UUID,
    ) -> ReservationServiceDetail:
        return await self.get(id_, True)
