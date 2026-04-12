"""Defines an abstract base class for working with the Google Calendar API."""

import asyncio
import datetime as dt
from abc import ABC, abstractmethod
from typing import Any

from core import settings
from core.application.exceptions import (
    Entity,
    EntityNotFoundError,
    ExternalAPIError,
    PermissionDeniedError,
)
from core.schemas.google_calendar import (
    CalendarImportResult,
    GoogleCalendarCalendar,
    GoogleCalendarEvent,
    GoogleCalendarEventCreate,
)
from fastapi import status
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import HttpRequest
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
    async def get_all_calendars(self) -> list[GoogleCalendarCalendar]:
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
    async def get_event(self, calendar_id: str, event_id: str) -> GoogleCalendarEvent:
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

    @abstractmethod
    async def get_acl(self, calendar_id: str) -> dict:
        """
        Retrieve the Access Control List (ACL) of a Google Calendar.

        :param calendar_id: The ID of the Google Calendar.

        :return: A dictionary containing ACL rules for the calendar.
        """

    @abstractmethod
    async def subscribe(self, calendar_id: str) -> None:
        """
        Subscribe the service account to a Google Calendar.

        :param calendar_id: The ID of the Google Calendar to subscribe to.
        """

    @abstractmethod
    async def subscribe_calendars(
        self,
        calendar_ids: list[str],
    ) -> list[CalendarImportResult]:
        """
        Subscribe the service account to multiple Google Calendars.

        :param calendar_ids: List of Google Calendar IDs to subscribe to.

        :return: List of results describing the outcome for each calendar.
        """


class GoogleCalendarService(AbstractGoogleCalendarService):
    """Service implementation for interacting with the Google Calendar API."""

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_info(
            settings.GOOGLE.INFO,
            scopes=settings.GOOGLE.SCOPES,
        )

        self.service = build(
            "calendar",
            "v3",
            credentials=credentials,
            cache_discovery=False,
        )

        self.service_account_email = settings.GOOGLE.CLIENT_EMAIL

    async def get_calendar(self, calendar_id: str) -> GoogleCalendarCalendar:
        request = self.service.calendars().get(calendarId=calendar_id)
        response = await self._execute_safe(
            request,
            error_message="Failed to fetch calendar from Google Calendar.",
            not_found=(
                Entity.CALENDAR,
                calendar_id,
                "The calendar does not exist in Google Calendar.",
            ),
        )

        return GoogleCalendarCalendar(**response)

    async def create_calendar(self, summary: str) -> GoogleCalendarCalendar:
        calendar_body = {
            "summary": summary,  # Title of the new calendar
            "timeZone": "Europe/Prague",  # Set your desired timezone
        }

        create_request = self.service.calendars().insert(body=calendar_body)
        created_calendar_data = await self._execute_safe(
            create_request,
            error_message="Failed to create calendar in Google Calendar.",
        )

        created_calendar = GoogleCalendarCalendar(**created_calendar_data)

        await self._execute_safe(
            self.service.acl().insert(
                calendarId=created_calendar.id,
                body={
                    "role": "owner",
                    "scope": {
                        "type": "user",
                        "value": settings.MAIL.USERNAME,
                    },
                },
                sendNotifications=True,
            ),
            error_message="Failed to assign owner.",
        )

        await self._execute_safe(
            self.service.acl().insert(
                calendarId=created_calendar.id,
                body={
                    "role": "reader",
                    "scope": {
                        "type": "default",
                    },
                },
                sendNotifications=False,
            ),
            error_message="Failed to make calendar public.",
        )

        return created_calendar

    async def get_all_calendars(self) -> list[GoogleCalendarCalendar]:
        request = self.service.calendarList().list()
        response = await self._execute_safe(
            request,
            error_message="Failed to list Google calendars.",
        )
        calendars = response.get("items", [])

        return [GoogleCalendarCalendar(**calendar) for calendar in calendars]

    async def user_has_calendar_access(self, calendar_id: str) -> None:
        request = self.service.calendarList().list()
        response = await self._execute_safe(
            request,
            error_message="Failed to get calendars in Google Calendar.",
        )

        calendar_list = response.get("items", [])

        if not any(cal["id"] == calendar_id for cal in calendar_list):
            message = "You don't have access to this calendar in Google Calendar."
            raise PermissionDeniedError(message)

    async def insert_event(
        self, calendar_id: str, event_body: GoogleCalendarEventCreate
    ) -> GoogleCalendarEvent:
        request = self.service.events().insert(
            calendarId=calendar_id,
            body=event_body.model_dump(by_alias=True),
        )
        response = await self._execute_safe(
            request,
            error_message="Failed to create event in Google Calendar.",
        )

        return GoogleCalendarEvent(**response)

    async def get_event(self, calendar_id: str, event_id: str) -> GoogleCalendarEvent:
        request = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id,
        )
        response = await self._execute_safe(
            request,
            error_message="Failed to fetch event from Google Calendar.",
            not_found=(
                Entity.EVENT,
                event_id,
                "The event does not exist in Google Calendar.",
            ),
        )

        return GoogleCalendarEvent(**response)

    async def update_event(
        self, calendar_id: str, event_id: str, body: GoogleCalendarEvent
    ) -> GoogleCalendarEvent:
        request = self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=body.model_dump(by_alias=True),
        )

        response = await self._execute_safe(
            request,
            error_message="Failed to update event in Google Calendar.",
            not_found=(
                Entity.EVENT,
                event_id,
                "The event does not exist in Google Calendar.",
            ),
        )

        return GoogleCalendarEvent(**response)

    async def delete_event(self, calendar_id: str, event_id: str) -> None:
        request = self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
        )
        await self._execute_safe(
            request,
            error_message="Failed to delete event in Google Calendar.",
            not_found=(
                Entity.EVENT,
                event_id,
                "The event does not exist in Google Calendar.",
            ),
        )

    async def fetch_events_in_time_range(
        self, calendar_id: str, start_time: dt.datetime, end_time: dt.datetime
    ) -> list[dict]:
        prague = timezone("Europe/Prague")
        start_time_str = prague.localize(start_time).isoformat()
        end_time_str = prague.localize(end_time).isoformat()

        request = self.service.events().list(
            calendarId=calendar_id,
            timeMin=start_time_str,
            timeMax=end_time_str,
            singleEvents=True,
            orderBy="startTime",
            timeZone="Europe/Prague",
        )

        response = await self._execute_safe(
            request,
            error_message="Failed to fetch events from Google Calendar.",
        )

        return response.get("items", [])

    async def get_acl(self, calendar_id: str) -> dict:
        request = self.service.acl().list(calendarId=calendar_id)

        return await self._execute_safe(
            request,
            error_message="Failed to fetch calendar ACL.",
        )

    async def subscribe(self, calendar_id: str) -> None:
        request = self.service.calendarList().insert(body={"id": calendar_id})

        await self._execute_safe(
            request,
            error_message="Failed to subscribe to calendar.",
        )

    async def subscribe_calendars(
        self,
        calendar_ids: list[str],
    ) -> list[CalendarImportResult]:

        results: list[CalendarImportResult] = []

        existing_ids = {cal.id for cal in await self.get_all_calendars()}

        for calendar_id in calendar_ids:
            # 1. check already subscribed
            if calendar_id in existing_ids:
                results.append(
                    CalendarImportResult(
                        id=calendar_id,
                        status="already_exists",
                    )
                )
                continue

            # 2. check ACL
            acl = await self.get_acl(calendar_id)
            role = self._extract_role(acl, self.service_account_email)

            if role not in {"owner", "writer"}:
                results.append(
                    CalendarImportResult(
                        id=calendar_id,
                        status="skipped_no_access",
                        role=role,
                    )
                )
                continue

            # 3. subscribe
            await self.subscribe(calendar_id)

            # 4. fetch metadata (optional but useful)
            calendar = await self.get_calendar(calendar_id)

            results.append(
                CalendarImportResult(
                    id=calendar_id,
                    status="subscribed",
                    role=role,
                    summary=calendar.summary,
                )
            )

        return results

    async def _execute_safe(
        self,
        request: HttpRequest,
        *,
        error_message: str,
        not_found: tuple[Entity, str, str] | None = None,
    ) -> Any:
        """
        Execute a Google API request safely in a thread pool.

        :param request: Google API request object.
        :param error_message: Generic error message for failures.
        :param not_found: Optional tuple (Entity, entity_id, message) for 404 mapping.
        """
        try:
            return await asyncio.to_thread(request.execute)

        except HttpError as exc:
            if not_found and int(exc.resp.status) == status.HTTP_404_NOT_FOUND:
                entity, entity_id, message = not_found
                raise EntityNotFoundError(
                    entity=entity,
                    entity_id=entity_id,
                    message=message,
                ) from exc

            raise ExternalAPIError(
                message=error_message,
                error_detail=str(exc),
            ) from exc

    def _extract_role(self, acl: dict, email: str) -> str | None:
        """
        Extract role of a given user/service account from ACL response.

        Returns None if no matching rule found.
        """
        for rule in acl.get("items", []):
            scope = rule.get("scope", {})

            if scope.get("value") == email:
                return rule.get("role")

        return None
