"""Defines an abstract base class for working with the Google Calendar API."""

import asyncio
import datetime as dt
from typing import Any

from application.ports.providers.calendar import CalendarProvider
from core.bootstrap.exceptions import (
    Entity,
    EntityNotFoundError,
    ExternalAPIError,
    PermissionDeniedError,
)
from fastapi import status
from googleapiclient.errors import HttpError
from googleapiclient.http import HttpRequest
from infrastructure.calendar.google import (
    CalendarImportResult,
    GoogleCalendarCalendar,
    GoogleCalendarEvent,
    GoogleCalendarEventCreate,
)
from pytz import timezone


class GoogleCalendarProvider(CalendarProvider):
    """Provider implementation for interacting with the Google Calendar API."""

    def __init__(self, client: Any, service_account_email: str, mail_username: str):
        self.client = client
        self.service_account_email = service_account_email
        self.mail_username = mail_username

    async def get_calendar(self, calendar_id: str) -> GoogleCalendarCalendar:
        request = self.client.calendars().get(calendarId=calendar_id)
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

        create_request = self.client.calendars().insert(body=calendar_body)
        created_calendar_data = await self._execute_safe(
            create_request,
            error_message="Failed to create calendar in Google Calendar.",
        )

        created_calendar = GoogleCalendarCalendar(**created_calendar_data)

        await self._execute_safe(
            self.client.acl().insert(
                calendarId=created_calendar.id,
                body={
                    "role": "owner",
                    "scope": {
                        "type": "user",
                        "value": self.mail_username,
                    },
                },
                sendNotifications=True,
            ),
            error_message="Failed to assign owner.",
        )

        await self._execute_safe(
            self.client.acl().insert(
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
        request = self.client.calendarList().list()
        response = await self._execute_safe(
            request,
            error_message="Failed to list Google calendars.",
        )
        calendars = response.get("items", [])

        return [GoogleCalendarCalendar(**calendar) for calendar in calendars]

    async def user_has_calendar_access(self, calendar_id: str) -> None:
        request = self.client.calendarList().list()
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
        request = self.client.events().insert(
            calendarId=calendar_id,
            body=event_body.model_dump(by_alias=True),
        )
        response = await self._execute_safe(
            request,
            error_message="Failed to create event in Google Calendar.",
        )

        return GoogleCalendarEvent(**response)

    async def get_event(self, calendar_id: str, event_id: str) -> GoogleCalendarEvent:
        request = self.client.events().get(
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
        request = self.client.events().update(
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
        request = self.client.events().delete(
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

        request = self.client.events().list(
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
        request = self.client.acl().list(calendarId=calendar_id)

        return await self._execute_safe(
            request,
            error_message="Failed to fetch calendar ACL.",
        )

    async def subscribe(self, calendar_id: str) -> None:
        request = self.client.calendarList().insert(body={"id": calendar_id})

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
