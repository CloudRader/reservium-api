"""
This module defines an abstract base class AbstractEventService that work with Event.
Test variant
"""
from typing import Any, Annotated
from abc import ABC, abstractmethod
from services.utils import control_conditions_and_permissions, \
    ready_event
from fastapi import Depends

from schemas import EventCreate, User, InformationFromIS
from db import get_db
from crud import CRUDCalendar
from sqlalchemy.orm import Session


# pylint: disable=too-few-public-methods
# reason: Methods will be added in the next versions of the program
class AbstractEventService(ABC):
    """
    This abstract class defines the interface for an event service.
    """

    @abstractmethod
    def post_event(self, event_input: EventCreate, is_buk: InformationFromIS,
                   user: User, google_calendar_service) -> Any:
        """
        Post event in google calendar.
        :param event_input: EventThat me need to post.
        :param is_buk: Information about user from IS.
        :param user: User object in db.
        :param google_calendar_service: Google Calendar service.

        :returns Event json object: the created event or exception otherwise.
        """


class EventService(AbstractEventService):
    """
    Class EventService represent service that work with Event
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.calendar_crud = CRUDCalendar(db)

    # pylint: disable=no-member
    # reason: The googleapiclient.discovery.build function
    # dynamically creates the events attribute, which is not easily
    # understood by static code analysis tools like pylint.
    def post_event(self, event_input: EventCreate, is_buk: InformationFromIS, user: User,
                   google_calendar_service) -> Any:
        calendar = self.calendar_crud.get_by_reservation_type(event_input.reservation_type)

        if not calendar:
            return None

        message = control_conditions_and_permissions(user, is_buk, event_input,
                                                     google_calendar_service, calendar)

        if message != "Access":
            return message

        event_body = ready_event(calendar, event_input, is_buk)

        if event_input.guests > calendar.max_people:
            google_calendar_service.events().insert(calendarId='primary', body=event_body).execute()
            return {"message": "Too many people!"
                               "You need get permission from the dormitory head, "
                               "after you will be automatically created a reservation or "
                               "will be canceled with explanation of the reason from the manager."}

        event = google_calendar_service.events().insert(calendarId=calendar.calendar_id,
                                                        body=event_body).execute()

        print(f"Event created {event.get('htmlLink')}")

        return event
