"""
Define the repository port interface for Event domain entities.

This module establishes the contract for CRUD and query operations on Event
entities, decoupled from database-specific implementation details.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from application.ports.repositories import BaseRepository
from domain.entities import Event
from domain.enums import EventState


class EventRepository(BaseRepository[Event], ABC):
    """
    Repository port interface for Event domain entities.

    Establishes abstract operations specific to Events, extending the base
    repository interface.
    """

    @abstractmethod
    async def get(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> Event | None:
        """
        Retrieve a single record by its id_.

        If include_removed is True retrieve a single record
        including marked as deleted.
        """

    @abstractmethod
    async def get_current_event_for_user(self, user_id: UUID) -> Event | None:
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
    ) -> list[Event]:
        """
        Retrieve events for the given reservation service aliases.

        :param aliases: List of reservation service aliases to filter events by.
        :param event_state: Event state of the event.
        :param past: Filter for event time. `True` for past events, `False` for future events.
            `None` to fetch all events (no time filtering).

        :return: Matching list of Event.
        """

    @abstractmethod
    async def get_overlapping_events(
        self,
        calendar_ids: list[UUID],
        start_time: datetime,
        end_time: datetime,
    ) -> list[Event]:
        """
        Retrieve events that overlap with the given time range for specific calendars.

        :param calendar_ids: List of calendar IDs to check.
        :param start_time: Start of the time range.
        :param end_time: End of the time range.

        :return: List of overlapping events.
        """
