"""
Define CRUD operations for the User model.

Includes an abstract base class (AbstractCRUDUser) and a concrete
implementation (CRUDUser) using SQLAlchemy.
"""

from datetime import datetime
from uuid import UUID

from application.ports.repositories import UserRepository
from application.schemas import UserCreate, UserUpdate
from infrastructure.database.sqlalchemy.models import CalendarModel, EventModel, UserModel
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class SQLAlchemyUserRepository(
    SQLAlchemyBaseRepository[UserModel, UserCreate, UserUpdate], UserRepository
):
    """
    Concrete class for CRUD operations specific to the User model.

    It extends the abstract AbstractCRUDUser class and implements the required methods
    for querying and manipulating User instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(UserModel, db)
        self.event_model = EventModel

    async def get_by_username(self, username: str) -> UserModel | None:
        stmt = select(self.model).filter(self.model.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_provider_id(self, provider_id: str) -> UserModel | None:
        stmt = select(self.model).filter(self.model.provider_id == provider_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_events_by_user_id(
        self,
        id_: UUID,
        page: int = 1,
        limit: int = 20,
        past: bool | None = None,
    ) -> list[EventModel]:
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
        return list(result.scalars().all())
