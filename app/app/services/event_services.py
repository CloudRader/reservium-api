"""
This module defines an abstract base class AbstractEventService that work with Event.
Test variant
"""
import datetime as dt
from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Any
from services.utils import type_of_reservation, get_events, check_membership, ready_event

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
        # Check of the membership
        if not check_membership(services):
            return {"message": "You are not member of the club!"}

        service = build("calendar", "v3", credentials=creds)

        calendar = type_of_reservation(event_input.reservation_type)

        check_collision = get_events(service,
                                     event_input.start_datetime,
                                     event_input.end_datetime, calendar)

        if len(check_collision) > 0:
            return {"message": "There's already a reservation for that time"}

        event = ready_event(calendar, event_input, user, room)

        event = service.events().insert(calendarId=calendar["calendar_id"], body=event).execute()

        print(f"Event created {event.get('htmlLink')}")

        return event
