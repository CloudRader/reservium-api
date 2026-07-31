"""
SQLAlchemy implementation of the UserRepository port.

This module adapts the UserRepository port to SQLAlchemy, handling database
operations for User domain entities.
"""

from application.ports.repositories import UserRepository
from domain.entities import User
from infrastructure.database.sqlalchemy.mappers import UserDBMapper
from infrastructure.database.sqlalchemy.models import UserModel
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyUserRepository(SQLAlchemyBaseRepository[User], UserRepository):
    """
    SQLAlchemy adapter implementing the UserRepository port.

    Handles persistence operations for User domain entities using SQLAlchemy.
    """

    def __init__(self, db: AsyncSession, mapper: UserDBMapper):
        super().__init__(UserModel, db, mapper)

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
