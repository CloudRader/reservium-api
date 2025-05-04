"""
This module defines the CRUD operations for the Event model, including an
abstract base class (AbstractCRUDEvent) and a concrete implementation (CRUDEvent)
using SQLAlchemy.
"""
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import EventModel
from schemas import EventCreateToDb, EventUpdate
from crud import CRUDBase


class AbstractCRUDEvent(CRUDBase[
                            EventModel,
                            EventCreateToDb,
                            EventUpdate
                        ], ABC):
    """
    Abstract class for CRUD operations specific to the Event model.
    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Event instances.
    """

    @abstractmethod
    async def get_by_user_id(
            self, user_id: int,
    ) -> list[EventModel] | None:
        """
        Retrieves the Events instance by user id.

        :param user_id: user id of the events.

        :return: Events with user id equal
        to user id or None if no such events exists.
        """


class CRUDEvent(AbstractCRUDEvent):
    """
    Concrete class for CRUD operations specific to the Event model.
    It extends the abstract AbstractCRUDEvent class and implements the required methods
    for querying and manipulating Event instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(EventModel, db)

    async def get_by_user_id(
            self, user_id: int
    ) -> list[EventModel] | None:
        stmt = select(self.model).filter(
            self.model.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
