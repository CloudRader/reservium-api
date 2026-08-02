"""
SQLAlchemy implementation of the ReservationServiceRepository port.

This module adapts the ReservationServiceRepository port to SQLAlchemy, handling database
operations for ReservationService domain entities.
"""

from application.ports.repositories import ReservationServiceRepository
from domain.entities import ReservationService
from infrastructure.database.sqlalchemy.mappers import (
    EventDBMapper,
    ReservationServiceDBMapper,
)
from infrastructure.database.sqlalchemy.models import (
    CalendarModel,
    EventModel,
    ReservationServiceModel,
)
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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
