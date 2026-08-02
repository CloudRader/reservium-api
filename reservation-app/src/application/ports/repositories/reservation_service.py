"""
Define the repository port interface for ReservationService domain entities.

This module establishes the contract for CRUD and query operations on ReservationService
entities, decoupled from database-specific implementation details.
"""

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, runtime_checkable
from uuid import UUID

from application.ports.repositories import BaseRepository
from domain.entities import ReservationService


@runtime_checkable
class HasReservationServiceId(Protocol):
    """Protocol for models that have a reservation_service_id field."""

    reservation_service_id: UUID


T = TypeVar("T", bound=HasReservationServiceId)


class ReservationServiceRepository(BaseRepository[ReservationService,], ABC):
    """
    Repository port interface for ReservationService domain entities.

    Establishes abstract operations specific to ReservationServices, extending the base
    repository interface.
    """

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationService | None:
        """
        Retrieve a ReservationService instance by its name.

        :param name: The name of the ReservationService.
        :param include_removed: Include removed object or not.

        :return: The ReservationService instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationService | None:
        """
        Retrieve a ReservationService instance by its service alias.

        :param alias: The alias of the ReservationService.
        :param include_removed: Include removed object or not.

        :return: The ReservationService instance if found, None otherwise.
        """

    @abstractmethod
    async def get_all_aliases(self) -> list[str]:
        """
        Retrieve all aliases from all ReservationServices.

        :return: list of aliases.
        """

    @abstractmethod
    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationService]:
        """
        Retrieve a public ReservationService instance.

        :param include_removed: Include removed object or not.

        :return: The public ReservationService instance if found, None otherwise.
        """
