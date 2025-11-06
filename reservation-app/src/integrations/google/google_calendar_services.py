"""Defines an abstract base class for working with the Google Calendar API."""

import datetime as dt
from abc import ABC, abstractmethod

from core.application.exceptions import (
    BaseAppError,
    Entity,
    EntityNotFoundError,
    ExternalAPIError,
    PermissionDeniedError,
)
from core.schemas.google_calendar import (
    GoogleCalendarCalendar,
    GoogleCalendarEvent,
    GoogleCalendarEventCreate,
)
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from integrations.google.google_auth import auth_google
from pytz import timezone


class AbstractGoogleCalendarService(ABC):
    """Interface for a service interacting with the Google Calendar API."""

    @abstractmethod
    async def get_calendar(self, calendar_id: str) -> GoogleCalendarCalendar:
        """
        Retrieve a Google Calendar by its ID.

        :param calendar_id: The ID of the Google Calendar.

        :return: The calendar object if found.
        """

    @abstractmethod
    async def create_calendar(self, summary: str) -> GoogleCalendarCalendar:
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
    async def user_has_calendar_access(self, calendar_id: str) -> None:
        """
        Check if the authenticated user has access to the specified Google Calendar.

        This method retrieves the list of calendars accessible by the user and verifies
        whether the given `calendar_id` is among them.

        :param calendar_id: The ID of the calendar to check access for.
        """

    @abstractmethod
    async def insert_event(
        self, calendar_id: str, event_body: GoogleCalendarEventCreate
    ) -> GoogleCalendarEvent:
        """
        Insert an event into a specific Google Calendar.

        :param calendar_id: The ID of the Google Calendar.
        :param event_body: Dictionary describing the event details.

        :return: The created event object.
        """

    @abstractmethod
    async def get_event(self, calendar_id: str, event_id: str) -> dict:
        """
        Retrieve a specific event from a Google Calendar.

        :param calendar_id: The ID of the calendar containing the event.
        :param event_id: The ID of the event to retrieve.

        :return: The event object if found.
        """

    @abstractmethod
    async def update_event(
        self, calendar_id: str, event_id: str, body: GoogleCalendarEvent
    ) -> GoogleCalendarEvent:
        """
        Update an existing event in a specific Google Calendar.

        :param calendar_id: The ID of the calendar containing the event.
        :param event_id: The ID of the event to update.
        :param body: A dictionary representing the updated event details.

        :return: The updated event object.
        """

    @abstractmethod
    async def delete_event(self, calendar_id: str, event_id: str) -> None:
        """
        Delete an event from a specific Google Calendar.

        :param calendar_id: The ID of the calendar containing the event.
        :param event_id: The ID of the event to delete.

        :return: A response confirming the deletion.
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

    async def get_calendar(self, calendar_id: str) -> GoogleCalendarCalendar:
        try:
            return GoogleCalendarCalendar(
                **self.service.calendars().get(calendarId=calendar_id).execute()
            )
        except HttpError as exc:
            raise EntityNotFoundError(
                entity=Entity.CALENDAR,
                entity_id=calendar_id,
                message="The calendar does not exist in Google Calendar.",
            ) from exc

    async def create_calendar(self, summary: str) -> GoogleCalendarCalendar:
        try:
            calendar_body = {
                "summary": summary,  # Title of the new calendar
                "timeZone": "Europe/Prague",  # Set your desired timezone
            }
            created_calendar = GoogleCalendarCalendar(
                **self.service.calendars().insert(body=calendar_body).execute()
            )

            rule = {
                "role": "reader",  # Role is 'reader' for read-only public access
                "scope": {"type": "default"},  # 'default' means public access
            }
            self.service.acl().insert(
                calendarId=created_calendar.id,
                body=rule,
                sendNotifications=False,
            ).execute()

            return created_calendar
        except HttpError as exc:
            raise BaseAppError("Can't create calendar in Google Calendar.") from exc

    async def get_all_calendars(self) -> list[GoogleCalendarCalendar]:
        try:
            calendars_dict = self.service.calendarList().list().execute().get("items", [])
            return [GoogleCalendarCalendar(**calendar) for calendar in calendars_dict]
        except HttpError as exc:
            raise BaseAppError("Failed to list Google calendars.") from exc

    async def user_has_calendar_access(self, calendar_id: str) -> None:
        try:
            calendar_list = self.service.calendarList().list().execute().get("items", [])
            if not any(cal["id"] == calendar_id for cal in calendar_list):
                raise PermissionDeniedError(
                    "You don't have access to this calendar in Google Calendar."
                )
        except HttpError as exc:
            raise ExternalAPIError(
                message="Failed to get calendars in Google Calendar.",
                error_detail=str(exc),
            ) from exc

    async def insert_event(
        self, calendar_id: str, event_body: GoogleCalendarEventCreate
    ) -> GoogleCalendarEvent:
        try:
            return GoogleCalendarEvent(
                **self.service.events()
                .insert(calendarId=calendar_id, body=event_body.model_dump(by_alias=True))
                .execute()
            )
        except HttpError as exc:
            raise ExternalAPIError(
                message="Failed to create event in Google Calendar.",
                error_detail=str(exc),
            ) from exc

    async def get_event(self, calendar_id: str, event_id: str) -> GoogleCalendarEvent:
        try:
            return GoogleCalendarEvent(
                **self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )
        except HttpError as exc:
            if exc.status_code == 404:
                raise EntityNotFoundError(
                    entity=Entity.EVENT,
                    entity_id=event_id,
                    message="The event does not exist in Google Calendar.",
                ) from exc
            raise ExternalAPIError(
                message="Failed to fetch event from Google Calendar.",
                error_detail=str(exc),
            ) from exc

    async def update_event(
        self, calendar_id: str, event_id: str, body: GoogleCalendarEvent
    ) -> GoogleCalendarEvent:
        try:
            return GoogleCalendarEvent(
                **self.service.events()
                .update(
                    calendarId=calendar_id, eventId=event_id, body=body.model_dump(by_alias=True)
                )
                .execute()
            )
        except HttpError as exc:
            if exc.status_code == 404:
                raise EntityNotFoundError(
                    entity=Entity.EVENT,
                    entity_id=event_id,
                    message="The event does not exist in Google Calendar.",
                ) from exc
            raise ExternalAPIError(
                message="Failed to update event in Google Calendar.",
                error_detail=str(exc),
            ) from exc

    async def delete_event(self, calendar_id: str, event_id: str) -> None:
        try:
            return self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        except HttpError as exc:
            if exc.status_code == 404:
                raise EntityNotFoundError(
                    entity=Entity.EVENT,
                    entity_id=event_id,
                    message="The event does not exist in Google Calendar.",
                ) from exc
            raise ExternalAPIError(
                message="Failed to delete event in Google Calendar.",
                error_detail=str(exc),
            ) from exc

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
