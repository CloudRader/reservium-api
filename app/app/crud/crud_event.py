"""
This module defines the CRUD operations for the Event model, including an
abstract base class (AbstractCRUDEvent) and a concrete implementation (CRUDEvent)
using SQLAlchemy.
"""
from datetime import datetime
from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from models import EventModel, EventState, CalendarModel
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

    @abstractmethod
    async def get_by_event_state_by_reservation_service_id(
            self, reservation_service_id: UUID,
            event_state: EventState,
    ) -> list[EventModel]:
        """
        Retrieves the Events instance by reservation service id.

        :param reservation_service_id: reservation service id of the events.
        :param event_state: event state of the event.

        :return: Events with reservation service id equal
        to reservation service id or empty list if no such events exists.
        """

    @abstractmethod
    async def confirm_event(
            self, uuid: str | None,
    ) -> EventModel | None:
        """
        Confirm event.

        :param uuid: The ID of the event to confirm.

        :return: the updated Event.
        """

    @abstractmethod
    async def get_current_event_for_user(
            self, user_id: int
    ) -> EventModel | None:
        """
        Retrieves the current event for the given user where the current
        time is between start_datetime and end_datetime.

        :param user_id: ID of the user.

        :return: Matching Event or None.
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
        stmt = (select(self.model).filter(self.model.user_id == user_id)
                .order_by(self.model.start_datetime.desc()))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_event_state_by_reservation_service_id(
            self, reservation_service_id: UUID,
            event_state: EventState,
    ) -> list[EventModel]:
        stmt = (
            select(self.model)
            .join(CalendarModel, self.model.calendar_id == CalendarModel.id)
            .filter(
                CalendarModel.reservation_service_id == reservation_service_id,
                self.model.event_state == event_state
            )
            .options(joinedload(self.model.calendar))
            .order_by(self.model.start_datetime.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def confirm_event(
            self, uuid: str | None,
    ) -> EventModel | None:
        if uuid is None:
            return None
        stmt = select(self.model).filter(
            self.model.id == uuid)
        result = await self.db.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        obj.event_state = EventState.CONFIRMED
        self.db.add(obj)
        await self.db.commit()
        return obj

    async def get_current_event_for_user(
            self, user_id: int
    ) -> EventModel | None:
        now = datetime.now()

        stmt = (
            select(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.start_datetime <= now,
                self.model.end_datetime >= now
            )
            .order_by(self.model.start_datetime.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
