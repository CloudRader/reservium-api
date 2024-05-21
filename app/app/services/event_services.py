"""
This module defines an abstract base class AbstractEventService that work with Event.
Test variant
"""
from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Any, Annotated
from services.utils import control_conditions_and_permissions, \
    ready_event
from fastapi import Depends

from schemas import EventCreate, UserIS, Room, User
from db import get_db
from crud import CRUDCalendar
from sqlalchemy.orm import Session


class AbstractEventService(ABC):
    """
    This abstract class defines the interface for an event service.
    """

    @abstractmethod
    def post_event(self, event_input: EventCreate, user_is: UserIS, user: User,
                   room: Room, creds, services) -> Any:
        """
        Post document in google calendar.
        :param event_input: EventThat me need to post.
        :param user_is:
        :param user:
        :param room:
        :param creds:
        :param services:

        :returns Event json object: the created event or exception otherwise.
        """


class EventService(AbstractEventService):
    """
    Class EventService represent service that work with Event
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.calendar_crud = CRUDCalendar(db)

    def post_event(self, event_input: EventCreate, user_is: UserIS, user: User,
                   room: Room, creds, services) -> Any:
        google_calendar_service = build("calendar", "v3", credentials=creds)

        calendar = self.calendar_crud.get_by_reservation_type(event_input.reservation_type)

        message = control_conditions_and_permissions(user, services, event_input, google_calendar_service, calendar)

        if message != "Access":
            return message

        event = ready_event(calendar, event_input, user_is, room)

        event = google_calendar_service.events().insert(calendarId=calendar.calendar_id, body=event).execute()

        print(f"Event created {event.get('htmlLink')}")

        return event
