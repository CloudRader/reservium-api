"""
Define CRUD operations for the ReservationService model.

Includes an abstract base class (AbstractCRUDReservationService) and a concrete
implementation (CRUDReservationService) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, runtime_checkable
from uuid import UUID

from core.models import CalendarModel, EventModel, EventState, ReservationServiceModel
from core.schemas import ReservationServiceCreate, ReservationServiceUpdate
from crud import CRUDBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select


@runtime_checkable
class HasReservationServiceId(Protocol):
    """Protocol for models that have a reservation_service_id field."""

    reservation_service_id: UUID


T = TypeVar("T", bound=HasReservationServiceId)


class AbstractCRUDReservationService(
    CRUDBase[
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


class CRUDReservationService(AbstractCRUDReservationService):
    """
    Concrete class for CRUD operations specific to the ReservationService model.

    It extends the abstract AbstractCRUDReservationService class and implements
    the required methods for querying and manipulating ReservationService instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(ReservationServiceModel, db)

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        stmt = select(self.model).filter(self.model.name == name)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        stmt = select(self.model).filter(self.model.alias == alias)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        stmt = select(self.model).filter(self.model.room_id == room_id)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_aliases(self) -> list[str]:
        stmt = select(self.model.alias)
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationServiceModel]:
        stmt = select(self.model).filter(self.model.public)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_related_entities_by_reservation_service_id(
        self,
        model: type[T],
        reservation_service_id: UUID,
        include_removed: bool = False,
    ) -> list[T]:
        stmt: Select = select(model).where(
            getattr(model, "reservation_service_id") == reservation_service_id  # noqa: B009
        )
        if include_removed:
            stmt = stmt.execution_options(include_deleted=include_removed)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_events_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        event_state: EventState | None = None,
    ) -> list[EventModel]:
        stmt = (
            select(EventModel)
            .join(CalendarModel, EventModel.calendar_id == CalendarModel.id)
            .filter(CalendarModel.reservation_service_id == reservation_service_id)
            .options(joinedload(EventModel.calendar))
            .order_by(EventModel.start_datetime.desc())
        )

        if event_state is not None:
            stmt = stmt.filter(EventModel.event_state == event_state)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
