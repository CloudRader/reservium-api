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
