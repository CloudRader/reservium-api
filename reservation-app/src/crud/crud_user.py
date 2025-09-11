"""
Define CRUD operations for the User model.

Includes an abstract base class (AbstractCRUDUser) and a concrete
implementation (CRUDUser) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from datetime import datetime

from core.models import CalendarModel, EventModel, UserModel
from core.schemas import UserCreate, UserUpdate
from core.schemas.event import EventDetail, EventTimeline
from crud import CRUDBase
from sqlalchemy import case, select
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
    async def get_events_by_user_id(self, id_: int) -> list[EventModel]:
        """
        Fetch related events by id_.

        :param id_: ID of the User.

        :return: List of related events of type `model`.
        """

    @abstractmethod
    async def get_events_by_user_filter_past_and_upcoming(
        self,
        id_: int,
    ) -> EventTimeline:
        """
        Retrieve events for a given user, split into past and upcoming categories.

        :param id_: ID of the User.

        :return: EventTimeline containing two lists of EventLite objects:
             ``past`` and ``upcoming``.
        """


class CRUDUser(AbstractCRUDUser):
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

    async def get_events_by_user_id(self, id_: int) -> list[EventModel]:
        stmt = (
            select(self.event_model)
            .options(
                joinedload(self.event_model.calendar).joinedload(CalendarModel.reservation_service)
            )
            .order_by(self.event_model.reservation_start.desc())
            .where(self.event_model.user_id == id_)
        )
        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_events_by_user_filter_past_and_upcoming(
        self,
        id_: int,
    ) -> EventTimeline:
        now = datetime.now()

        stmt = (
            select(
                self.event_model,
                case(
                    (self.event_model.reservation_end < now, "past"),
                    (self.event_model.reservation_start > now, "upcoming"),
                ).label("status"),
            )
            .options(
                joinedload(self.event_model.calendar).joinedload(CalendarModel.reservation_service)
            )
            .filter(self.event_model.user_id == id_)
            .order_by(self.event_model.reservation_start.asc())
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        grouped: dict = {"past": [], "upcoming": []}
        for event, status in rows:
            grouped[status].append(EventDetail.model_validate(event))

        return EventTimeline(**grouped)
