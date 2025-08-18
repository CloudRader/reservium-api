"""
Define CRUD operations for the User model.

Includes an abstract base class (AbstractCRUDUser) and a concrete
implementation (CRUDUser) using SQLAlchemy.
"""

from abc import ABC, abstractmethod

from core.models import CalendarModel, EventModel, UserModel
from core.schemas import UserCreate, UserUpdate
from crud import CRUDBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class AbstractCRUDUser(CRUDBase[UserModel, UserCreate, UserUpdate], ABC):
    """
    Abstract class for CRUD operations specific to the User model.

    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating User instances.
    """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserModel | None:
        """
        Retrieve a User instance by its username.

        :param username: The username of the User.

        :return: The User instance if found, None otherwise.
        """

    @abstractmethod
    async def get_events_by_user_id(self, user_id: int) -> list[EventModel]:
        """
        Fetch related events by user_id.

        :param user_id: UUID of the User.

        :return: List of related events of type `model`.
        """


class CRUDUser(AbstractCRUDUser):
    """
    Concrete class for CRUD operations specific to the User model.

    It extends the abstract AbstractCRUDUser class and implements the required methods
    for querying and manipulating User instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(UserModel, db)

    async def get_by_username(self, username: str) -> UserModel | None:
        stmt = select(self.model).filter(self.model.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_events_by_user_id(self, user_id: int) -> list[EventModel]:
        stmt = (
            select(EventModel)
            .options(joinedload(EventModel.calendar).joinedload(CalendarModel.reservation_service))
            .where(EventModel.user_id == user_id)
        )
        result = await self.db.execute(stmt)

        return list(result.scalars().all())
