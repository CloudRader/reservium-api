"""
This module defines the CRUD operations for the User model, including an
abstract base class (AbstractCRUDUser) and a concrete implementation (CRUDUser)
using SQLAlchemy.
"""
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import UserModel
from schemas import UserCreate, UserUpdate

from crud import CRUDBase


class AbstractCRUDUser(CRUDBase[
                           UserModel,
                           UserCreate,
                           UserUpdate
                       ], ABC):
    """
    Abstract class for CRUD operations specific to the User model.
    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating User instances.
    """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserModel | None:
        """
        Retrieves a User instance by its username.

        :param username: The username of the User.

        :return: The User instance if found, None otherwise.
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
