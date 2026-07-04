"""Defines an abstract base class for working with the Calendar Provider."""

import datetime as dt
from abc import ABC, abstractmethod

from infrastructure.google import (
    CalendarImportResult,
    GoogleCalendarCalendar,
    GoogleCalendarEvent,
    GoogleCalendarEventCreate,
)


class CalendarProvider(ABC):
    """Interface for a service interacting with the Calendar Provider."""

    @abstractmethod
    async def get_calendar(self, calendar_id: str) -> GoogleCalendarCalendar:
        """
        Retrieve a Calendar by its ID.

        :param calendar_id: The ID of the Calendar.

        :return: The calendar object if found.
        """

    @abstractmethod
    async def create_calendar(self, summary: str) -> GoogleCalendarCalendar:
        """
        Create a new Calendar and make it publicly readable.

        :param summary: The summary (title) of the new calendar.

        :return: The created calendar object.
        """

    @abstractmethod
    async def get_all_calendars(self) -> list[GoogleCalendarCalendar]:
        """
        Retrieve all calendars from the authenticated account.

        :return: A list of calendar objects.
        """

    @abstractmethod
    async def user_has_calendar_access(self, calendar_id: str) -> None:
        """
        Check if the authenticated user has access to the specified Calendar.

        This method retrieves the list of calendars accessible by the user and verifies
        whether the given `calendar_id` is among them.

        :param calendar_id: The ID of the calendar to check access for.
        """

    @abstractmethod
    async def insert_event(
        self, calendar_id: str, event_body: GoogleCalendarEventCreate
    ) -> GoogleCalendarEvent:
        """
        Insert an event into a specific Calendar.

        :param calendar_id: The ID of the Calendar.
        :param event_body: Dictionary describing the event details.

        :return: The created event object.
        """

    @abstractmethod
    async def get_event(self, calendar_id: str, event_id: str) -> GoogleCalendarEvent:
        """
        Retrieve a specific event from a Calendar.

        :param calendar_id: The ID of the calendar containing the event.
        :param event_id: The ID of the event to retrieve.

        :return: The event object if found.
        """

    @abstractmethod
    async def update_event(
        self, calendar_id: str, event_id: str, body: GoogleCalendarEvent
    ) -> GoogleCalendarEvent:
        """
        Update an existing event in a specific Calendar.

        :param calendar_id: The ID of the calendar containing the event.
        :param event_id: The ID of the event to update.
        :param body: A dictionary representing the updated event details.

        :return: The updated event object.
        """

    @abstractmethod
    async def delete_event(self, calendar_id: str, event_id: str) -> None:
        """
        Delete an event from a specific Calendar.

        :param calendar_id: The ID of the calendar containing the event.
        :param event_id: The ID of the event to delete.

        :return: A response confirming the deletion.
        """

    @abstractmethod
    async def fetch_events_in_time_range(
        self, calendar_id: str, start_time: dt.datetime, end_time: dt.datetime
    ) -> list[dict]:
        """
        Fetch all events from the specified Calendar between the given start and end times.

        :param calendar_id: ID of the Calendar to query.
        :param start_time: The start of the time range.
        :param end_time: The end of the time range.

        :return: List of calendar events within the specified time range.
        """

    @abstractmethod
    async def get_acl(self, calendar_id: str) -> dict:
        """
        Retrieve the Access Control List (ACL) of a Calendar.

        :param calendar_id: The ID of the Calendar.

        :return: A dictionary containing ACL rules for the calendar.
        """

    @abstractmethod
    async def subscribe(self, calendar_id: str) -> None:
        """
        Subscribe the service account to a Calendar.

        :param calendar_id: The ID of the Calendar to subscribe to.
        """

    @abstractmethod
    async def subscribe_calendars(
        self,
        calendar_ids: list[str],
    ) -> list[CalendarImportResult]:
        """
        Subscribe the service account to multiple Calendars.

        :param calendar_ids: List of Calendar IDs to subscribe to.

        :return: List of results describing the outcome for each calendar.
        """
