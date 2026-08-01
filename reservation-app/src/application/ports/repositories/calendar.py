"""
Define the repository port interface for Calendar domain entities.

This module establishes the contract for CRUD and query operations on Calendar
entities, decoupled from database-specific implementation details.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from application.ports.repositories import BaseRepository
from domain.entities import Calendar, MiniService


class CalendarRepository(BaseRepository[Calendar], ABC):
    """
    Repository port interface for Calendar domain entities.

    Establishes abstract operations specific to Calendars, extending the base
    repository interface.
    """

    @abstractmethod
    async def get_with_collisions(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> Calendar | None:
        """
        Retrieve a single record by its id_ with collisions.

        If include_removed is True retrieve a single record
        including marked as deleted.
        """

    @abstractmethod
    async def create_with_mini_services_and_collisions(
        self,
        calendar: Calendar,
        mini_services: list[MiniService],
        collision_ids: list[UUID],
    ) -> Calendar:
        """
        Create a new Calendar instance with associated mini services and collisions.

        :param calendar: Domain Calendar entity to create.
        :param mini_services: List of MiniService domain objects to associate.
        :param collision_ids: List of collion ids.

        :return: The created Calendar domain instance.
        """

    @abstractmethod
    async def update_with_mini_services_and_collisions(
        self,
        calendar: Calendar,
        mini_services: list[MiniService],
        collision_ids: list[UUID],
    ) -> Calendar:
        """
        Update an existing Calendar instance including mini services and collisions.

        :param calendar: The updated Domain Calendar entity.
        :param mini_services: List of MiniService domain objects to associate.
        :param collision_ids: List of collion ids.

        :return: The updated Calendar domain instance.
        """

    @abstractmethod
    async def get_by_reservation_type(
        self,
        reservation_type: str,
        include_removed: bool = False,
    ) -> Calendar | None:
        """
        Retrieve a Calendar instance by its reservation type.

        :param reservation_type: The reservation type of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_provider_id(
        self,
        provider_id: str,
        include_removed: bool = False,
    ) -> Calendar | None:
        """
        Retrieve a Calendar instance by its provider ID.

        :param provider_id: The provider ID of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        include_removed: bool = False,
    ) -> list[Calendar]:
        """
        Fetch related calendars for a specific reservation service.

        :param reservation_service_id: ID of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: List of related calendars.
        """

    @abstractmethod
    async def get_by_reservation_service_ids(
        self,
        reservation_service_ids: list[UUID],
        include_removed: bool = False,
    ) -> list[Calendar]:
        """
        Fetch related calendars for multiple reservation service IDs in bulk.

        :param reservation_service_ids: List of Reservation Service IDs.
        :param include_removed: Include removed objects or not.

        :return: List of related calendars for all specified service IDs.
        """
