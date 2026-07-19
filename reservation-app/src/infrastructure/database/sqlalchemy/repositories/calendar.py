"""
SQLAlchemy implementation of the CalendarRepository port.

This module adapts the CalendarRepository port to SQLAlchemy, handling database
operations for Calendar domain entities.
"""

from typing import Any
from uuid import UUID

from application.ports.repositories import CalendarRepository
from application.schemas import CalendarCreate, CalendarUpdate
from domain.entities import Calendar, MiniService
from infrastructure.database.sqlalchemy.mappers import CalendarDBMapper
from infrastructure.database.sqlalchemy.models import CalendarModel, MiniServiceModel
from infrastructure.database.sqlalchemy.models.calendar_collisions_association import (
    CalendarCollisionAssociation,
)
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class SQLAlchemyCalendarRepository(
    SQLAlchemyBaseRepository[Calendar, CalendarCreate, CalendarUpdate], CalendarRepository
):
    """
    SQLAlchemy adapter implementing the CalendarRepository port.

    Handles persistence operations for Calendar domain entities using SQLAlchemy.
    """

    def __init__(self, db: AsyncSession, mapper: CalendarDBMapper):
        super().__init__(CalendarModel, db, mapper)

    async def get_with_collisions(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> Calendar | None:
        stmt = (
            select(self.model)
            .execution_options(include_deleted=include_removed)
            .filter(self.model.id == id_)
        )
        stmt = stmt.options(selectinload(CalendarModel.collisions))
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return self.mapper.to_entity(db_obj) if db_obj else None

    async def create_with_mini_services_and_collisions(
        self,
        calendar_create: CalendarCreate | dict[str, Any],
        mini_services: list[MiniService],
    ) -> Calendar:
        obj_in_data = (
            calendar_create if isinstance(calendar_create, dict) else calendar_create.model_dump()
        )

        collision_ids = obj_in_data.pop("collision_ids", [])
        obj_in_data.pop("mini_services", None)

        db_obj = self.model(**obj_in_data)
        db_obj.mini_services = mini_services

        self.db.add(db_obj)
        await self.db.flush()

        if collision_ids:
            await self._add_symmetric_collisions(db_obj, collision_ids)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return self.mapper.to_entity(db_obj)

    async def update_with_mini_services_and_collisions(
        self,
        obj: Calendar,
        obj_in: CalendarUpdate | dict[str, Any],
        mini_services: list[MiniService],
    ) -> Calendar:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        collision_ids = update_data.pop("collision_ids", None)
        update_data.pop("mini_services", None)

        stmt = select(self.model).filter(self.model.id == obj.id)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        mini_service_ids = [m.id for m in mini_services]
        if mini_service_ids:
            stmt_ms = select(MiniServiceModel).filter(MiniServiceModel.id.in_(mini_service_ids))
            res_ms = await self.db.execute(stmt_ms)
            db_obj.mini_services = list(res_ms.scalars().all())
        else:
            db_obj.mini_services = []

        self.db.add(db_obj)
        await self.db.flush()

        if collision_ids is not None:
            stmt_delete = delete(CalendarCollisionAssociation).where(
                (CalendarCollisionAssociation.calendar_id == db_obj.id)
                | (CalendarCollisionAssociation.collides_with_id == db_obj.id)
            )

            await self.db.execute(stmt_delete)
            if collision_ids:
                await self._add_symmetric_collisions(db_obj, collision_ids)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return self.mapper.to_entity(db_obj)

    async def get_by_reservation_type(
        self,
        reservation_type: str,
        include_removed: bool = False,
    ) -> Calendar | None:
        stmt = select(self.model).where(self.model.reservation_type == reservation_type)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()
        return self.mapper.to_entity(db_obj) if db_obj else None

    async def get_by_provider_id(
        self,
        provider_id: str,
        include_removed: bool = False,
    ) -> Calendar | None:
        stmt = select(self.model).where(self.model.provider_id == provider_id)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()
        return self.mapper.to_entity(db_obj) if db_obj else None

    async def _add_symmetric_collisions(
        self,
        calendar: CalendarModel,
        collision_ids: list[str],
    ) -> None:
        """Add symmetric collisions for a given calendar."""
        collision_ids = [cid for cid in collision_ids if cid != calendar.id]

        collisions_bulk = []
        for cid in collision_ids:
            collisions_bulk.append({"calendar_id": calendar.id, "collides_with_id": cid})
            collisions_bulk.append({"calendar_id": cid, "collides_with_id": calendar.id})

        stmt = insert(CalendarCollisionAssociation).values(collisions_bulk)
        await self.db.execute(stmt)
