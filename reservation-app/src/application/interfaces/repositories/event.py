"""
Define CRUD operations for the Event model.

Includes an abstract base class (AbstractCRUDEvent) and a concrete
implementation (CRUDEvent) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from api.schemas import EventCreate, EventUpdate
from application.interfaces.repositories import BaseRepository
from domain.models import EventModel, EventState


class EventRepository(BaseRepository[EventModel, EventCreate, EventUpdate], ABC):
    """
    Abstract class for CRUD operations specific to the Event model.

    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Event instances.
    """

    @abstractmethod
    async def get(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> EventModel | None:
        """
        Retrieve a single record by its id_.

        If include_removed is True retrieve a single record
        including marked as deleted.
        """

    @abstractmethod
    async def get_current_event_for_user(self, user_id: UUID) -> EventModel | None:
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
        past: bool | None = None,
    ) -> list[EventModel]:
        """
        Retrieve events for the given reservation service aliases.

        :param aliases: List of reservation service aliases to filter events by.
        :param event_state: Event state of the event.
        :param past: Filter for event time. `True` for past events, `False` for future events.
            `None` to fetch all events (no time filtering).

        :return: Matching list of EventModel.
        """

    @abstractmethod
    async def get_overlapping_events(
        self,
        calendar_ids: list[UUID],
        start_time: datetime,
        end_time: datetime,
    ) -> list[EventModel]:
        """
        Retrieve events that overlap with the given time range for specific calendars.

        :param calendar_ids: List of calendar IDs to check.
        :param start_time: Start of the time range.
        :param end_time: End of the time range.

        :return: List of overlapping events.
        """
