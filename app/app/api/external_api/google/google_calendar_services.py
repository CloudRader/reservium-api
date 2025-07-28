"""Defines an abstract base class for working with the Google Calendar API."""

import datetime as dt
from abc import ABC, abstractmethod

from api import BaseAppError, Entity, EntityNotFoundError
from api.external_api.google.google_auth import auth_google
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytz import timezone


class AbstractGoogleCalendarService(ABC):
    """Interface for a service interacting with the Google Calendar API."""

    @abstractmethod
    async def get_calendar(self, calendar_id: str) -> dict:
        """
        Retrieve a Google Calendar by its ID.

        :param calendar_id: The ID of the Google Calendar.

        :return: The calendar object if found.
        """

    @abstractmethod
    async def create_calendar(self, summary: str) -> dict:
        """
        Create a new Google Calendar and make it publicly readable.

        :param summary: The summary (title) of the new calendar.

        :return: The created calendar object.
        """

    @abstractmethod
    async def get_all_calendars(self) -> list[dict]:
        """
        Retrieve all calendars from the authenticated Google account.

        :return: A list of calendar objects.
        """

    @abstractmethod
    async def insert_event(self, calendar_id: str, event_body: dict) -> dict:
        """
        Insert an event into a specific Google Calendar.

        :param calendar_id: The ID of the Google Calendar.
        :param event_body: Dictionary describing the event details.

        :return: The created event object.
        """

    @abstractmethod
    async def fetch_events_in_time_range(
        self, calendar_id: str, start_time: dt.datetime, end_time: dt.datetime
    ) -> list[dict]:
        """
        Fetch all events from the specified Google Calendar between the given start and end times.

        :param calendar_id: ID of the Google Calendar to query.
        :param start_time: The start of the time range.
        :param end_time: The end of the time range.

        :return: List of calendar events within the specified time range.
        """


class GoogleCalendarService(AbstractGoogleCalendarService):
    """Service implementation for interacting with the Google Calendar API."""

    def __init__(self):
        self.service = build("calendar", "v3", credentials=auth_google(None))

    async def get_calendar(self, calendar_id: str) -> dict:
        try:
            return self.service.calendars().get(calendarId=calendar_id).execute()
        except HttpError as exc:
            raise EntityNotFoundError(
                entity=Entity.CALENDAR,
                entity_id=calendar_id,
                message="The calendar does not exist in Google Calendar.",
            ) from exc

    async def create_calendar(self, summary: str) -> dict:
        try:
            calendar_body = {
                "summary": summary,  # Title of the new calendar
                "timeZone": "Europe/Prague",  # Set your desired timezone
            }
            created_calendar = self.service.calendars().insert(body=calendar_body).execute()
            calendar_id = created_calendar.get("id")

            rule = {
                "role": "reader",  # Role is 'reader' for read-only public access
                "scope": {"type": "default"},  # 'default' means public access
            }
            self.service.acl().insert(calendarId=calendar_id, body=rule).execute()

            return created_calendar
        except HttpError as exc:
            raise BaseAppError("Can't create calendar in Google Calendar.") from exc

    async def get_all_calendars(self) -> list[dict]:
        try:
            return self.service.calendarList().list().execute().get("items", [])
        except HttpError as exc:
            raise BaseAppError("Failed to list Google calendars.") from exc

    async def insert_event(self, calendar_id: str, event_body: dict) -> dict:
        return self.service.events().insert(calendarId=calendar_id, body=event_body).execute()

    async def fetch_events_in_time_range(
        self, calendar_id: str, start_time: dt.datetime, end_time: dt.datetime
    ) -> list[dict]:
        prague = timezone("Europe/Prague")
        start_time_str = prague.localize(start_time).isoformat()
        end_time_str = prague.localize(end_time).isoformat()

        events_result = (
            self.service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start_time_str,
                timeMax=end_time_str,
                singleEvents=True,
                orderBy="startTime",
                timeZone="Europe/Prague",
            )
            .execute()
        )
        return events_result.get("items", [])
