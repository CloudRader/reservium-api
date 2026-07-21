"""
Define the repository port interface for ReservationService domain entities.

This module establishes the contract for CRUD and query operations on ReservationService
entities, decoupled from database-specific implementation details.
"""

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, runtime_checkable
from uuid import UUID

from application.ports.repositories import BaseRepository
from domain.entities import Event, ReservationService
from domain.enums import EventState


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

    @abstractmethod
    async def get_related_entities_by_reservation_service_id(
        self,
        model: type[T],
        reservation_service_id: UUID,
        include_removed: bool = False,
    ) -> list[T]:
        """
        Fetch related entities by reservation_service_id.

        :param model: The SQLAlchemy model class to query.
        :param reservation_service_id: UUID of the ReservationService.
        :param include_removed: Whether to include soft-deleted records.

        :return: List of related entities.
        """

    @abstractmethod
    async def get_events_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        event_state: EventState | None = None,
    ) -> list[Event]:
        """
        Fetch related events by reservation_service_id.

        :param reservation_service_id: UUID of the ReservationService.
        :param event_state: Event state of the event.

        :return: List of related events.
        """
