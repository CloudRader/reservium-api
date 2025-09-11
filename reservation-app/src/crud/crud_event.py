"""
Define CRUD operations for the Event model.

Includes an abstract base class (AbstractCRUDEvent) and a concrete
implementation (CRUDEvent) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from core.models import CalendarModel, EventModel, EventState, ReservationServiceModel
from core.schemas import EventLite, EventUpdate
from crud import CRUDBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class AbstractCRUDEvent(CRUDBase[EventModel, EventLite, EventUpdate], ABC):
    """
    Abstract class for CRUD operations specific to the Event model.

    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Event instances.
    """

    @abstractmethod
    async def get(
        self,
        id_: str | int,
        include_removed: bool = False,
    ) -> EventModel | None:
        """
        Retrieve a single record by its id_.

        If include_removed is True retrieve a single record
        including marked as deleted.
        """

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: int,
    ) -> list[EventModel] | None:
        """
        Retrieve the Events instance by user id.

        :param user_id: user id of the events.

        :return: Events with user id equal
        to user id or None if no such events exists.
        """

    @abstractmethod
    async def confirm_event(
        self,
        id_: str | None,
    ) -> EventModel | None:
        """
        Confirm event.

        :param id_: The ID of the event to confirm.

        :return: the updated Event.
        """

    @abstractmethod
    async def get_current_event_for_user(self, user_id: int) -> EventModel | None:
        """
        Retrieve the current event for the given user where the current.

        Time is between start_datetime and end_datetime.

        :param user_id: ID of the user.

        :return: Matching Event or None.
        """

    @abstractmethod
    async def get_events_by_aliases(
        self,
        aliases: list[str],
        event_state: EventState | None = None,
    ) -> list[EventModel]:
        """
        Retrieve events for the given reservation service aliases.

        :param aliases: List of reservation service aliases to filter events by.
        :param event_state: Event state of the event.

        :return: Matching list of EventModel.
        """


class CRUDEvent(AbstractCRUDEvent):
    """
    Concrete class for CRUD operations specific to the Event model.

    It extends the abstract AbstractCRUDEvent class and implements the required methods
    for querying and manipulating Event instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(EventModel, db)
        self.state = EventState
        self.calendar_model = CalendarModel
        self.reservation_service_model = ReservationServiceModel

    async def get(
        self,
        id_: str | int,
        include_removed: bool = False,
    ) -> EventModel | None:
        if id_ is None:
            return None
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.calendar).joinedload(self.calendar_model.reservation_service),
                joinedload(self.model.user),
            )
            .execution_options(include_deleted=include_removed)
            .filter(self.model.id == id_)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> list[EventModel] | None:
        stmt = (
            select(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.start_datetime.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def confirm_event(
        self,
        id_: str | None,
    ) -> EventModel | None:
        obj = await self._check_id_and_return_obj_from_db_by_id(id_)
        if obj is None:
            return None
        obj.event_state = self.state.CONFIRMED
        self.db.add(obj)
        await self.db.commit()
        return obj

    async def get_current_event_for_user(self, user_id: int) -> EventModel | None:
        now = datetime.now()

        stmt = (
            select(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.start_datetime <= now,
                self.model.end_datetime >= now,
            )
            .order_by(self.model.reservation_start.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_events_by_aliases(
        self,
        aliases: list[str],
        event_state: EventState | None = None,
    ) -> list[EventModel]:
        stmt = (
            select(self.model)
            .join(self.calendar_model, self.model.calendar_id == self.calendar_model.id)
            .join(
                self.reservation_service_model,
                self.calendar_model.reservation_service_id == self.reservation_service_model.id,
            )
            .filter(self.reservation_service_model.alias.in_(aliases))
            .options(
                joinedload(self.model.calendar).joinedload(self.calendar_model.reservation_service),
                joinedload(self.model.user),
            )
            .order_by(self.model.reservation_start.desc())
        )

        if event_state is not None:
            stmt = stmt.filter(self.model.event_state == event_state)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
