"""
Define CRUD operations for the ReservationService model.

Includes an abstract base class (AbstractCRUDReservationService) and a concrete
implementation (CRUDReservationService) using SQLAlchemy.
"""

from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable
from uuid import UUID

from application.ports.repositories import ReservationServiceRepository
from application.schemas import ReservationServiceCreate, ReservationServiceUpdate
from infrastructure.database.sqlalchemy.models import (
    CalendarModel,
    EventModel,
    EventState,
    ReservationServiceModel,
)
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.sql import Select


@runtime_checkable
class HasReservationServiceId(Protocol):
    """Protocol for models that have a reservation_service_id field."""

    reservation_service_id: UUID


T = TypeVar("T", bound=HasReservationServiceId)


class SQLAlchemyReservationServiceRepository(
    SQLAlchemyBaseRepository[
        ReservationServiceModel, ReservationServiceCreate, ReservationServiceUpdate
    ],
    ReservationServiceRepository,
):
    """
    Concrete class for CRUD operations specific to the ReservationService model.

    It extends the abstract AbstractCRUDReservationService class and implements
    the required methods for querying and manipulating ReservationService instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(ReservationServiceModel, db)
        self.calendar_model = CalendarModel
        self.event_model = EventModel

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
            select(self.event_model)
            .join(self.calendar_model, self.event_model.calendar_id == self.calendar_model.id)
            .filter(self.calendar_model.reservation_service_id == reservation_service_id)
            .options(
                joinedload(self.event_model.calendar).joinedload(
                    self.calendar_model.reservation_service
                ),
                joinedload(self.event_model.user),
            )
            .order_by(self.event_model.reservation_start.desc())
        )

        if event_state is not None:
            stmt = stmt.filter(self.event_model.event_state == event_state)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
