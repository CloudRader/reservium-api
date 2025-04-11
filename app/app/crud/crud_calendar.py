"""
This module defines the CRUD operations for the Calendar model, including an
abstract base class (AbstractCRUDCalendar) and a concrete implementation (CRUDCalendar)
using SQLAlchemy.
"""
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import CalendarModel
from schemas import CalendarCreate, CalendarUpdate

from crud import CRUDBase


class AbstractCRUDCalendar(CRUDBase[
                               CalendarModel,
                               CalendarCreate,
                               CalendarUpdate
                           ], ABC):
    """
    Abstract class for CRUD operations specific to the Calendar model.
    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Calendar instances.
    """

    @abstractmethod
    async def get_by_reservation_type(self, reservation_type: str,
                                include_removed: bool = False) -> CalendarModel | None:
        """
        Retrieves a Calendar instance by its reservation type.

        :param reservation_type: The reservation type of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """


class CRUDCalendar(AbstractCRUDCalendar):
    """
    Concrete class for CRUD operations specific to the Calendar model.
    It extends the abstract AbstractCRUDCalendar class and implements the required methods
    for querying and manipulating Calendar instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(CalendarModel, db)

    async def get_by_reservation_type(self, reservation_type: str,
                                include_removed: bool = False) -> CalendarModel | None:
        stmt = select(self.model).where(self.model.reservation_type == reservation_type)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalars().first()
