"""
SQLAlchemy implementation of the MiniServiceRepository port.

This module adapts the MiniServiceRepository port to SQLAlchemy, handling database
operations for MiniService domain entities.
"""

from uuid import UUID

from application.ports.repositories import MiniServiceRepository
from domain.entities import MiniService
from infrastructure.database.sqlalchemy.mappers import MiniServiceDBMapper
from infrastructure.database.sqlalchemy.models import MiniServiceModel
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyMiniServiceRepository(SQLAlchemyBaseRepository[MiniService], MiniServiceRepository):
    """
    SQLAlchemy adapter implementing the MiniServiceRepository port.

    Handles persistence operations for MiniService domain entities using SQLAlchemy.
    """

    def __init__(self, db: AsyncSession, mapper: MiniServiceDBMapper):
        super().__init__(MiniServiceModel, db, mapper)

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniService | None:
        stmt = select(self.model).where(self.model.name == name)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return self.mapper.to_entity(db_obj) if db_obj else None

    async def get_names_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
    ) -> list[str]:
        stmt = select(self.model.name).where(
            self.model.reservation_service_id == reservation_service_id,
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_ids_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
    ) -> list[UUID]:
        stmt = select(self.model.id).where(
            self.model.reservation_service_id == reservation_service_id,
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        include_removed: bool = False,
    ) -> list[MiniService]:
        stmt = select(self.model).where(self.model.reservation_service_id == reservation_service_id)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=include_removed)

        result = await self.db.execute(stmt)
        return [self.mapper.to_entity(obj) for obj in result.scalars().all()]

    async def get_by_reservation_service_ids(
        self,
        reservation_service_ids: list[UUID],
        include_removed: bool = False,
    ) -> list[MiniService]:
        if not reservation_service_ids:
            return []

        stmt = select(self.model).where(
            self.model.reservation_service_id.in_(reservation_service_ids)
        )
        if include_removed:
            stmt = stmt.execution_options(include_deleted=include_removed)

        result = await self.db.execute(stmt)
        return [self.mapper.to_entity(obj) for obj in result.scalars().all()]

    async def get_by_calendar_ids(
        self,
        calendar_ids: list[UUID],
        include_removed: bool = False,
    ) -> list[MiniService]:
        if not calendar_ids:
            return []

        stmt = select(self.model).where(self.model.calendar_ids.in_(calendar_ids))
        if include_removed:
            stmt = stmt.execution_options(include_deleted=include_removed)

        result = await self.db.execute(stmt)
        return [self.mapper.to_entity(obj) for obj in result.scalars().all()]
