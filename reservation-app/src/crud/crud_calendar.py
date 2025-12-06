"""
Define CRUD operations for the Calendar model.

Includes an abstract base class (AbstractCRUDCalendar) and a concrete
implementation (CRUDCalendar) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from typing import Any

from core.models import CalendarModel, MiniServiceModel
from core.models.calendar_collisions_association import CalendarCollisionAssociationTable
from core.schemas import CalendarCreate, CalendarUpdate
from crud import CRUDBase
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


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
    async def get_with_collisions(
        self,
        id_: str | int,
        include_removed: bool = False,
    ) -> CalendarModel | None:
        """
        Retrieve a single record by its id_ with collisions.

        If include_removed is True retrieve a single record
        including marked as deleted.
        """

    @abstractmethod
    async def create_with_mini_services_and_collisions(
        self,
        calendar_create: CalendarCreate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
        """
        Create a new Calendar instance with associated mini services and collisions.

        This method extends the base create method by:
        - Attaching multiple MiniServiceModel instances to the created calendar.
        - Creating symmetric collision relationships with other Calendar instances
          as specified in the input.

        :param calendar_create: Data used to create the Calendar (schema or dict).
        :param mini_services: List of MiniServiceModel objects to associate with the calendar.

        :return: The created CalendarModel instance with mini services and collisions attached.
        """

    @abstractmethod
    async def update_with_mini_services_and_collisions(
        self,
        db_obj: CalendarModel,
        obj_in: CalendarUpdate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
        """
        Update an existing Calendar instance including mini services and collisions.

        This method extends the base update functionality by:
        - Replacing the existing mini services with the provided list.
        - Updating symmetric collision relationships for the calendar.
          Existing collisions are removed and replaced according to the input.

        :param db_obj: The existing CalendarModel instance to update.
        :param obj_in: Data to update the Calendar (schema or dict).
        :param mini_services: List of MiniServiceModel objects to associate with the calendar.

        :return: The updated CalendarModel instance with updated mini services and collisions.
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

    async def get_with_collisions(
        self,
        id_: str | int,
        include_removed: bool = False,
    ) -> CalendarModel | None:
        if id_ is None:
            return None
        stmt = (
            select(self.model)
            .execution_options(include_deleted=include_removed)
            .filter(self.model.id == id_)
        )
        stmt = stmt.options(selectinload(CalendarModel.collisions))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_with_mini_services_and_collisions(
        self,
        calendar_create: CalendarCreate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
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
        return db_obj

    async def update_with_mini_services_and_collisions(
        self,
        db_obj: CalendarModel,
        obj_in: CalendarUpdate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        collision_ids = update_data.pop("collision_ids", [])
        update_data.pop("mini_services", None)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.mini_services = mini_services

        self.db.add(db_obj)
        await self.db.flush()

        if collision_ids:
            stmt_delete = delete(CalendarCollisionAssociationTable).where(
                (CalendarCollisionAssociationTable.calendar_id == db_obj.id)
                | (CalendarCollisionAssociationTable.collides_with_id == db_obj.id)
            )

            await self.db.execute(stmt_delete)
            await self._add_symmetric_collisions(db_obj, collision_ids)

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

        if collisions_bulk:
            stmt = insert(CalendarCollisionAssociationTable).values(collisions_bulk)
            await self.db.execute(stmt)
