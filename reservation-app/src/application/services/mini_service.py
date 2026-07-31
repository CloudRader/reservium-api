"""
Define an abstract base class AbstractMiniServiceService.

This class works with Mini Service.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from application.mappers import MiniServiceMapper
from application.ports.repositories import MiniServiceRepository
from application.schemas import (
    MiniServiceCreate,
    MiniServiceSchema,
    MiniServiceUpdate,
)
from application.services import BaseService
from application.services.reservation_service import ReservationServiceService
from core.bootstrap.exceptions import (
    Entity,
    EntityNotFoundError,
)
from domain.entities import MiniService


class AbstractMiniServiceService(
    BaseService[
        MiniServiceSchema,
        MiniServiceRepository,
        MiniService,
        MiniServiceCreate,
        MiniServiceUpdate,
    ],
    ABC,
):
    """
    Abstract class defines the interface for a mini service ser.

    Provides CRUD operations for a specific MiniServiceModel.
    """

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniServiceSchema:
        """
        Retrieve a Mini Service instance by its name.

        :param name: The name of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance.
        """

    @abstractmethod
    async def get_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        include_removed: bool = False,
    ) -> list[MiniServiceSchema]:
        """
        Retrieve mini services by reservation service ID.

        :param reservation_service_id: The ID of the reservation service.
        :param include_removed: Optional flag to include removed mini services.
        :return: List of MiniServiceLite schemas linked to the reservation service.
        """


class MiniServiceService(AbstractMiniServiceService):
    """Class MiniServiceService represent service that work with Mini Service."""

    def __init__(
        self,
        mini_service_repository: MiniServiceRepository,
        reservation_service_service: ReservationServiceService,
        mapper: MiniServiceMapper,
    ):
        super().__init__(
            mini_service_repository,
            Entity.MINI_SERVICE,
            MiniServiceSchema,
            mapper,
        )
        self.reservation_service_service = reservation_service_service

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniServiceSchema:
        mini_service = await self.repo.get_by_name(name, include_removed)
        if mini_service is None:
            raise EntityNotFoundError(self.entity_name, name)
        return self.mapper.to_schema(mini_service)

    async def get_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        include_removed: bool = False,
    ) -> list[MiniServiceSchema]:
        mini_services = await self.repo.get_by_reservation_service_id(
            reservation_service_id, include_removed
        )
        return [self.mapper.to_schema(mini_service) for mini_service in mini_services]
