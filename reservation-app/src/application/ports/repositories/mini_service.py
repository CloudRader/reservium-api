"""
Define the repository port interface for MiniService domain entities.

This module establishes the contract for CRUD and query operations on MiniService
entities, decoupled from database-specific implementation details.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from application.ports.repositories import BaseRepository
from domain.entities import MiniService


class MiniServiceRepository(BaseRepository[MiniService], ABC):
    """
    Repository port interface for MiniService domain entities.

    Establishes abstract operations specific to MiniServices, extending the base
    repository interface.
    """

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniService | None:
        """
        Retrieve a MiniService instance by its name.

        :param name: The name of the MiniService.
        :param include_removed: Include removed object or not.

        :return: The MiniService instance if found, None otherwise.
        """

    @abstractmethod
    async def get_names_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
    ) -> list[str]:
        """
        Retrieve all names from all MiniServices by reservation service uuid.

        :param reservation_service_id: The uuid of the reservation service.

        :return: list of names.
        """

    @abstractmethod
    async def get_ids_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
    ) -> list[UUID]:
        """
        Retrieve all ids from all MiniServices by reservation service uuid.

        :param reservation_service_id: The uuid of the reservation service.

        :return: list of ids.
        """

    @abstractmethod
    async def get_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        include_removed: bool = False,
    ) -> list[MiniService]:
        """
        Fetch related mini services for a specific reservation service.

        :param reservation_service_id: ID of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: List of related mini services.
        """

    @abstractmethod
    async def get_by_reservation_service_ids(
        self,
        reservation_service_ids: list[UUID],
        include_removed: bool = False,
    ) -> list[MiniService]:
        """
        Fetch related mini services for multiple reservation service IDs in bulk.

        :param reservation_service_ids: List of Reservation Service IDs.
        :param include_removed: Include removed objects or not.

        :return: List of related mini services for all specified service IDs.
        """

    @abstractmethod
    async def get_by_calendar_id(
        self,
        calendar_id: UUID,
        include_removed: bool = False,
    ) -> list[MiniService]:
        """
        Fetch related mini services for a specific reservation service.

        :param calendar_id: ID of the Calendar.
        :param include_removed: Include removed object or not.

        :return: List of related mini services.
        """

    @abstractmethod
    async def get_by_calendar_ids(
        self,
        calendar_ids: list[UUID],
        include_removed: bool = False,
    ) -> list[MiniService]:
        """
        Fetch related mini services for multiple calendar IDs in bulk.

        :param calendar_ids: List of Calendar IDs.
        :param include_removed: Include removed objects or not.

        :return: List of related mini services for all specified calendar IDs.
        """
