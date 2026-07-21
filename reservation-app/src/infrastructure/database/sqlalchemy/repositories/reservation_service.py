"""
SQLAlchemy implementation of the ReservationServiceRepository port.

This module adapts the ReservationServiceRepository port to SQLAlchemy, handling database
operations for ReservationService domain entities.
"""

from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable
from uuid import UUID

from application.ports.repositories import ReservationServiceRepository
from domain.entities import Event, ReservationService
from infrastructure.database.sqlalchemy.mappers import (
    EventDBMapper,
    ReservationServiceDBMapper,
)
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
    SQLAlchemyBaseRepository[ReservationService], ReservationServiceRepository
):
    """
    SQLAlchemy adapter implementing the ReservationServiceRepository port.

    Handles persistence operations for ReservationService domain entities using SQLAlchemy.
    """

    def __init__(
        self,
        db: AsyncSession,
        mapper: ReservationServiceDBMapper,
        event_mapper: EventDBMapper,
    ):
        super().__init__(ReservationServiceModel, db, mapper)
        self.calendar_model = CalendarModel
        self.event_model = EventModel
        self.event_mapper = event_mapper

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationService | None:
        stmt = select(self.model).filter(self.model.name == name)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return self.mapper.to_entity(db_obj) if db_obj else None

    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationService | None:
        stmt = select(self.model).filter(self.model.alias == alias)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return self.mapper.to_entity(db_obj) if db_obj else None

    async def get_all_aliases(self) -> list[str]:
        stmt = select(self.model.alias)
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationService]:
        stmt = select(self.model).filter(self.model.public)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return [self.mapper.to_entity(obj) for obj in result.scalars().all()]

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
    ) -> list[Event]:
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
        return [self.event_mapper.to_entity(obj) for obj in result.scalars().all()]
