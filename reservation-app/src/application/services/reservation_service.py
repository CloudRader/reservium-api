"""
Define an abstract base class AbstractReservationServiceService.

This class works with Reservation Service.
"""

from abc import ABC, abstractmethod

from application.mappers import ReservationServiceMapper
from application.ports.repositories import (
    CalendarRepository,
    MiniServiceRepository,
    ReservationServiceRepository,
)
from application.schemas import (
    ReservationServiceCreate,
    ReservationServiceSchema,
    ReservationServiceUpdate,
)
from application.services import BaseService
from core.bootstrap.exceptions import (
    Entity,
    EntityNotFoundError,
)
from domain.entities import ReservationService


class AbstractReservationServiceService(
    BaseService[
        ReservationServiceSchema,
        ReservationServiceRepository,
        ReservationService,
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
    ) -> ReservationServiceSchema:
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
    ) -> ReservationServiceSchema:
        """
        Retrieve a Reservation Service instance by its name.

        :param name: The name of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance.
        """

    @abstractmethod
    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationServiceSchema]:
        """
        Retrieve a public Reservation Service instance.

        :param include_removed: Include removed object or not.

        :return: The public Reservation Service instance if found, None otherwise.
        """


class ReservationServiceService(AbstractReservationServiceService):
    """Class MiniServiceService represent service that work with Mini Service."""

    def __init__(
        self,
        reservation_service_repository: ReservationServiceRepository,
        calendar_repository: CalendarRepository,
        mini_service_repository: MiniServiceRepository,
        mapper: ReservationServiceMapper,
    ):
        super().__init__(
            reservation_service_repository,
            Entity.RESERVATION_SERVICE,
            ReservationServiceSchema,
            mapper,
        )
        self.calendar_repo = calendar_repository
        self.mini_service_repo = mini_service_repository

    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationServiceSchema:
        reservation_service = await self.repo.get_by_alias(alias, include_removed)
        if reservation_service is None:
            raise EntityNotFoundError(self.entity_name, alias)
        return self.mapper.to_schema(reservation_service)

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationServiceSchema:
        reservation_service = await self.repo.get_by_name(name, include_removed)
        if reservation_service is None:
            raise EntityNotFoundError(self.entity_name, name)
        return self.mapper.to_schema(reservation_service)

    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationServiceSchema]:
        services = await self.repo.get_public_services(include_removed)
        return [self.mapper.to_schema(service) for service in services]
