"""
This module defines an abstract base class AbstractEventService that work with Event.
Test variant
"""
from typing import Any, Annotated
from abc import ABC, abstractmethod
from services.utils import ready_event, first_standard_check, \
    dif_days_res, reservation_in_advance
from fastapi import Depends

from schemas import EventCreate, User, InformationFromIS, Calendar
from models import CalendarModel
from db import get_db
from crud import CRUDReservationService
from sqlalchemy.orm import Session


# pylint: disable=too-few-public-methods
# reason: Methods will be added in the next versions of the program
class AbstractEventService(ABC):
    """
    This abstract class defines the interface for an event service.
    """

    @abstractmethod
    def post_event(self, event_input: EventCreate, is_info: InformationFromIS,
                   user: User, calendar: Calendar) -> Any:
        """
        Post event in google calendar.
        :param event_input: Input data for creating the event.
        :param is_info: Information about user from IS.
        :param user: User object in db.
        :param calendar: Calendar object in db.

        :returns Event json object: the created event or exception otherwise.
        """


class EventService(AbstractEventService):
    """
    Class EventService represent service that work with Event
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.reservation_service_crud = CRUDReservationService(db)

    def post_event(
            self, event_input: EventCreate,
            is_info: InformationFromIS, user: User,
            calendar: Calendar
    ) -> Any:
        if not calendar:
            return {"message": "Calendar with that type not exist!"}

        message = self.__control_conditions_and_permissions(
            user, is_info, event_input, calendar)

        if message != "Access":
            return message

        return ready_event(calendar, event_input, is_info)

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
                                                event_input.start_datetime,
                                                event_input.end_datetime)
        if not standard_message == "Access":
            return standard_message

        if not calendar.more_than_max_people_with_permission and \
                event_input.guests > calendar.max_people:
            return {"message": f"You can't reserve this type of "
                               f"reservation for more than {calendar.max_people} people!"}

        # Choose user rules
        user_rules = self.__choose_user_rules(user, calendar)

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
