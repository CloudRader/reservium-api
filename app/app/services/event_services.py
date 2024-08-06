"""
This module defines an abstract base class AbstractEventService that work with Event.
Test variant
"""
from typing import Any, Annotated
from abc import ABC, abstractmethod
from services.utils import ready_event, first_standard_check, \
    control_available_reservation_time, get_events, \
    check_collision_time, dif_days_res, reservation_in_advance
from googleapiclient.discovery import build
from fastapi import Depends

from schemas import EventCreate, User, InformationFromIS
from models import CalendarModel
from db import get_db
from crud import CRUDCalendar, CRUDReservationService
from api import auth_google
from sqlalchemy.orm import Session


# pylint: disable=too-few-public-methods
# reason: Methods will be added in the next versions of the program
class AbstractEventService(ABC):
    """
    This abstract class defines the interface for an event service.
    """

    @abstractmethod
    def post_event(self, event_input: EventCreate, is_info: InformationFromIS,
                   user: User) -> Any:
        """
        Post event in google calendar.
        :param event_input: EventThat me need to post.
        :param is_info: Information about user from IS.
        :param user: User object in db.

        :returns Event json object: the created event or exception otherwise.
        """


class EventService(AbstractEventService):
    """
    Class EventService represent service that work with Event
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
        self.calendar_crud = CRUDCalendar(db)
        self.reservation_service_crud = CRUDReservationService(db)

    # pylint: disable=no-member
    # reason: The googleapiclient.discovery.build function
    # dynamically creates the events attribute, which is not easily
    # understood by static code analysis tools like pylint.
    def post_event(
            self, event_input: EventCreate,
            is_info: InformationFromIS, user: User
    ) -> Any:
        calendar = self.calendar_crud.get_by_reservation_type(event_input.reservation_type)
        if not calendar:
            return {"message": "Calendar with that type not exist!"}

        message = self.__control_conditions_and_permissions(
            user, is_info, event_input, calendar)

        if message != "Access":
            return message

        event_body = ready_event(calendar, event_input, is_info)

        if event_input.guests > calendar.max_people:
            self.google_calendar_service.events().insert(calendarId='primary',
                                                         body=event_body).execute()
            return {"message": "Too many people!"
                               "You need get permission from the dormitory head, "
                               "after you will be automatically created a reservation or "
                               "will be canceled with explanation of the reason from the manager."}

        # Check night reservation
        if not self.__choose_user_rules(user, calendar).night_time:
            if not control_available_reservation_time(event_input.start_datetime,
                                                      event_input.end_datetime):
                self.google_calendar_service.events().insert(calendarId='primary',
                                                             body=event_body).execute()
                return {"message": "Request for a night reservation has been sent to the manager, "
                                   "awaiting a response. Please note that the manager "
                                   "may reject a night reservation without giving a reason."}

        event = self.google_calendar_service.events().insert(calendarId=calendar.id,
                                                             body=event_body).execute()

        print(f"Event created {event.get('htmlLink')}")

        return event

    def __control_conditions_and_permissions(
            self, user: User,
            is_info: InformationFromIS,
            event_input: EventCreate,
            calendar: CalendarModel
    ) -> str | dict:
        """
        Check conditions and permissions for creating an event.

        :param user: User object in db.
        :param is_info: Information about user from IS.
        :param event_input: Input data for creating the event.
        :param calendar: Calendar object in db.
        ReservationService objects in db.

        :return: Message indicating whether access is granted or denied.
        """
        reservation_service = self.reservation_service_crud.get(
            calendar.reservation_service_id)

        # Check of the membership
        standard_message = first_standard_check(is_info, reservation_service,
                                                event_input.start_datetime)
        if not standard_message == "Access":
            return standard_message

        # Choose user rules
        user_rules = self.__choose_user_rules(user, calendar)

        # Check collision with other reservation
        check_collision: list = []
        collisions: list = calendar.collision_with_calendar
        collisions.append(calendar.id)
        if calendar.collision_with_calendar:
            for calendar_id in collisions:
                check_collision.extend(get_events(self.google_calendar_service,
                                                  event_input.start_datetime,
                                                  event_input.end_datetime,
                                                  calendar_id))

        if not check_collision_time(check_collision,
                                    event_input.start_datetime,
                                    event_input.end_datetime,
                                    calendar,
                                    self.google_calendar_service):
            return {"message": "There's already a reservation for that time."}

        # Reservation no more than 24 hours
        if not dif_days_res(event_input.start_datetime, event_input.end_datetime, user_rules):
            return {"message": "You can reserve on different day."}

        # Check reservation in advance and prior
        message = reservation_in_advance(event_input.start_datetime, user_rules)
        if not message == "Access":
            return message

        return "Access"

    def __choose_user_rules(
            self, user: User,
            calendar: CalendarModel
    ):
        """
        Choose user rules based on the calendar rules and user roles.

        :param user: User object in db.
        :param calendar: Calendar object in db.

        :return: Rules object.
        """
        reservation_service = self.reservation_service_crud.get(
            calendar.reservation_service_id)

        if not user.active_member:
            return calendar.club_member_rules
        if reservation_service.alias in user.roles:
            return calendar.manager_rules
        return calendar.active_member_rules
