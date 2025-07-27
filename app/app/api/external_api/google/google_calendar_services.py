"""Defines an abstract base class for working with the Google Calendar API."""

from abc import ABC, abstractmethod

from api import BaseAppError, Entity, EntityNotFoundError
from api.external_api.google.google_auth import auth_google
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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
            created_calendar = (
                self.service.calendars().insert(body=calendar_body).execute()
            )
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
