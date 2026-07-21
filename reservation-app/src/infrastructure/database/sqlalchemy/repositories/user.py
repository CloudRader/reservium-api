"""
SQLAlchemy implementation of the UserRepository port.

This module adapts the UserRepository port to SQLAlchemy, handling database
operations for User domain entities.
"""

from datetime import datetime
from uuid import UUID

from application.ports.repositories import UserRepository
from domain.entities import Event, User
from infrastructure.database.sqlalchemy.mappers import EventDBMapper, UserDBMapper
from infrastructure.database.sqlalchemy.models import CalendarModel, EventModel, UserModel
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class SQLAlchemyUserRepository(SQLAlchemyBaseRepository[User], UserRepository):
    """
    SQLAlchemy adapter implementing the UserRepository port.

    Handles persistence operations for User domain entities using SQLAlchemy.
    """

    def __init__(self, db: AsyncSession, mapper: UserDBMapper, event_mapper: EventDBMapper):
        super().__init__(UserModel, db, mapper)
        self.event_model = EventModel
        self.event_mapper = event_mapper

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(self.model).filter(self.model.username == username)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return self.mapper.to_entity(db_obj) if db_obj else None

    async def get_by_provider_id(self, provider_id: str) -> User | None:
        stmt = select(self.model).filter(self.model.provider_id == provider_id)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return self.mapper.to_entity(db_obj) if db_obj else None

    async def get_events_by_user_id(
        self,
        id_: UUID,
        page: int = 1,
        limit: int = 20,
        past: bool | None = None,
    ) -> list[Event]:
        now = datetime.now()

        stmt = (
            select(self.event_model)
            .options(
                joinedload(self.event_model.calendar).joinedload(CalendarModel.reservation_service)
            )
            .where(self.event_model.user_id == id_)
            .order_by(self.event_model.reservation_start.desc())
        )
        if past:
            stmt = stmt.where(self.event_model.reservation_end < now)
        elif past is False:
            stmt = stmt.where(self.event_model.reservation_start > now)

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        return [self.event_mapper.to_entity(obj) for obj in result.scalars().all()]
