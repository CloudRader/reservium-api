"""
SQLAlchemy implementation of the MiniServiceRepository port.

This module adapts the MiniServiceRepository port to SQLAlchemy, handling database
operations for MiniService domain entities.
"""

from uuid import UUID

from application.ports.repositories import MiniServiceRepository
from application.schemas import MiniServiceCreate, MiniServiceUpdate
from domain.entities import MiniService
from infrastructure.database.sqlalchemy.mappers import MiniServiceDBMapper
from infrastructure.database.sqlalchemy.models import MiniServiceModel
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyMiniServiceRepository(
    SQLAlchemyBaseRepository[MiniService, MiniServiceCreate, MiniServiceUpdate],
    MiniServiceRepository,
):
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

    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> MiniService | None:
        stmt = select(self.model).where(self.model.room_id == room_id)
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
