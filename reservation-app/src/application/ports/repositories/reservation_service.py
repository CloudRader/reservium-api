"""
Define CRUD operations for the ReservationService model.

Includes an abstract base class (AbstractCRUDReservationService) and a concrete
implementation (CRUDReservationService) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, runtime_checkable
from uuid import UUID

from api.schemas import ReservationServiceCreate, ReservationServiceUpdate
from application.ports.repositories import BaseRepository
from infrastructure.database.sqlalchemy.models import (
    EventModel,
    EventState,
    ReservationServiceModel,
)


@runtime_checkable
class HasReservationServiceId(Protocol):
    """Protocol for models that have a reservation_service_id field."""

    reservation_service_id: UUID


T = TypeVar("T", bound=HasReservationServiceId)


class ReservationServiceRepository(
    BaseRepository[
        ReservationServiceModel,
        ReservationServiceCreate,
        ReservationServiceUpdate,
    ],
    ABC,
):
    """
    Abstract class for CRUD operations specific to the ReservationService model.

    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating ReservationService instances.
    """

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        """
        Retrieve a Reservation Service instance by its name.

        :param name: The name of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        """
        Retrieve a Reservation Services instance by its service alias.

        :param alias: The alias of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        """
        Retrieve a Reservation Service instance by its room id.

        :param room_id: The room id of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_all_aliases(self) -> list[str]:
        """
        Retrieve all aliases from all Reservation Services.

        :return: list of aliases.
        """

    @abstractmethod
    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationServiceModel]:
        """
        Retrieve a public Reservation Service instance.

        :param include_removed: Include removed object or not.

        :return: The public Reservation Service instance if found, None otherwise.
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
        :param reservation_service_id: UUID of the Reservation Service.
        :param include_removed: Whether to include soft-deleted records.

        :return: List of related entities of type `model`.
        """

    @abstractmethod
    async def get_events_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        event_state: EventState | None = None,
    ) -> list[EventModel]:
        """
        Fetch related events by reservation_service_id.

        :param reservation_service_id: UUID of the Reservation Service.
        :param event_state: Event state of the event.

        :return: List of related events of type `model`.
        """
