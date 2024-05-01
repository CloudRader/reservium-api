"""
This module defines an abstract base class AbstractEventService that work with Event.
Test variant
"""
from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Any
from services.utils import type_of_reservation, control_conditions_and_permissions, \
    ready_event

from schemas import EventInput, UserIS, Room


class AbstractEventService(ABC):
    """
    This abstract class defines the interface for an event service.
    """

    @abstractmethod
    def post_event(self, event_input: EventInput, user: UserIS, room: Room, creds, services) -> Any:
        """
        Post document in google calendar.
        :param event_input: EventThat me need to post.
        :param user:
        :param room:
        :param creds:
        :param services:
        """


class EventService(AbstractEventService):

    def post_event(self, event_input: EventInput, user: UserIS, room: Room, creds, services) -> Any:
        service = build("calendar", "v3", credentials=creds)

        calendar = type_of_reservation(event_input.reservation_type)

        message = control_conditions_and_permissions(services, event_input, service, calendar)

        if message != "Access":
            return message

        event = ready_event(calendar, event_input, user, room)

        event = service.events().insert(calendarId=calendar["calendar_id"], body=event).execute()

        print(f"Event created {event.get('htmlLink')}")

        return event
