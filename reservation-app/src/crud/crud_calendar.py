"""
Define CRUD operations for the Calendar model.

Includes an abstract base class (AbstractCRUDCalendar) and a concrete
implementation (CRUDCalendar) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from typing import Any

from core.models import CalendarModel, MiniServiceModel
from core.schemas import CalendarCreate, CalendarUpdate
from crud import CRUDBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractCRUDCalendar(
    CRUDBase[CalendarModel, CalendarCreate, CalendarUpdate],
    ABC,
):
    """
    Abstract class for CRUD operations specific to the Calendar model.

    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Calendar instances.
    """

    @abstractmethod
    async def create_with_mini_services(
        self,
        calendar_create: CalendarCreate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
        """
        Create a new Calendar instance with associated mini services.

        This method is similar to the base `create` method but additionally
        attaches a list of `MiniServiceModel` instances to the created calendar.

        :param calendar_create: Data used to create the Calendar (schema or dict).
        :param mini_services: List of MiniServiceModel objects to associate with the calendar.

        :return: The created CalendarModel instance with mini services attached.
        """

    @abstractmethod
    async def update_with_mini_services(
        self,
        db_obj: CalendarModel,
        obj_in: CalendarUpdate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
        """
        Update an existing Calendar instance, including its associated mini services.

        This method extends the base `update` functionality by ensuring
        the provided list of `MiniServiceModel` objects replaces the existing
        mini services linked to the calendar.

        :param db_obj: The existing CalendarModel instance to update.
        :param obj_in: Data to update the Calendar (schema or dict).
        :param mini_services: List of MiniServiceModel objects to associate with the calendar.

        :return: The updated CalendarModel instance with updated mini services.
        """

    @abstractmethod
    async def get_by_reservation_type(
        self,
        reservation_type: str,
        include_removed: bool = False,
    ) -> CalendarModel | None:
        """
        Retrieve a Calendar instance by its reservation type.

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

    async def create_with_mini_services(
        self,
        calendar_create: CalendarCreate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
        obj_in_data = (
            calendar_create if isinstance(calendar_create, dict) else calendar_create.model_dump()
        )

        obj_in_data.pop("mini_services", None)
        db_obj = self.model(**obj_in_data)
        db_obj.mini_services = mini_services

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update_with_mini_services(
        self,
        db_obj: CalendarModel,
        obj_in: CalendarUpdate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        update_data.pop("mini_services", None)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.mini_services = mini_services

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_by_reservation_type(
        self,
        reservation_type: str,
        include_removed: bool = False,
    ) -> CalendarModel | None:
        stmt = select(self.model).where(self.model.reservation_type == reservation_type)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalars().first()
