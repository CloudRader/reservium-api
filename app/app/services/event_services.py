"""
This module defines an abstract base class AbstractEventService that work with Event.
"""
from typing import Any, Annotated
from abc import ABC, abstractmethod
from services.utils import ready_event, first_standard_check, \
    dif_days_res, reservation_in_advance
from services import CrudServiceBase
from fastapi import Depends

from schemas import EventCreate, User, InformationFromIS, Calendar, \
    EventCreateToDb, EventUpdate
from models import CalendarModel, EventModel, EventState
from db import db_session
from crud import CRUDReservationService, CRUDEvent
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession


# pylint: disable=too-few-public-methods
# reason: Methods will be added in the next versions of the program
class AbstractEventService(CrudServiceBase[
                               EventModel,
                               CRUDEvent,
                               EventCreateToDb,
                               EventUpdate,
                           ], ABC):
    """
    This abstract class defines the interface for an event service.
    """

    @abstractmethod
    async def post_event(self, event_input: EventCreate, is_info: InformationFromIS,
                         user: User, calendar: Calendar) -> Any:
        """
        Preparing for posting event in google calendar.
        :param event_input: Input data for creating the event.
        :param is_info: Information about user from IS.
        :param user: User object in db.
        :param calendar: Calendar object in db.

        :returns Event json object: the created event or exception otherwise.
        """

    @abstractmethod
    async def create_event(
            self, event_create: EventCreate,
            user: User,
            event_state: EventState,
            event_id: str
    ) -> EventModel | None:
        """
        Create an Event in the database.

        :param event_create: EventCreate Schema for create.
        :param user: the UserSchema for control permissions of the reservation service.
        :param event_state: State of the event.
        :param event_id: Event id in google calendar.

        :return: the created Event.
        """

    @abstractmethod
    async def get_by_user_id(
            self, user_id: int,
    ) -> list[Row[EventModel]] | None:
        """
        Retrieves the Events instance by user id.

        :param user_id: user id of the events.

        :return: Events with user id equal
        to user id or None if no such events exists.
        """


class EventService(AbstractEventService):
    """
    Class EventService represent service that work with Event
    """

    def __init__(self, db: Annotated[
        AsyncSession, Depends(db_session.scoped_session_dependency)]):
        super().__init__(CRUDEvent(db))
        self.reservation_service_crud = CRUDReservationService(db)

    async def post_event(
            self, event_input: EventCreate,
            is_info: InformationFromIS, user: User,
            calendar: Calendar
    ) -> Any:
        if not calendar:
            return {"message": "Calendar with that type not exist!"}

        message = await self.__control_conditions_and_permissions(
            user, is_info, event_input, calendar)

        if message != "Access":
            return message

        return ready_event(calendar, event_input, is_info)

    async def create_event(
            self, event_create: EventCreate,
            user: User,
            event_state: EventState,
            event_id: str
    ) -> EventModel | None:
        event_create_to_db = EventCreateToDb(
            id=event_id,
            start_datetime=event_create.start_datetime,
            end_datetime=event_create.end_datetime,
            purpose=event_create.purpose,
            guests=event_create.guests,
            email=event_create.email,
            event_state=event_state,
            user_id=user.id,
            calendar_id=event_create.reservation_type,
        )
        return await self.crud.create(event_create_to_db)

    async def get_by_user_id(
            self, user_id: int,
    ) -> list[Row[EventModel]] | None:
        return await self.crud.get_by_user_id(user_id)

    async def __control_conditions_and_permissions(
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
        reservation_service = await self.reservation_service_crud.get(
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
        user_rules = await self.__choose_user_rules(user, calendar)

        # Reservation no more than 24 hours
        if not dif_days_res(event_input.start_datetime, event_input.end_datetime, user_rules):
            return {"message": "You can reserve on different day."}

        # Check reservation in advance and prior
        message = reservation_in_advance(event_input.start_datetime, user_rules)
        if not message == "Access":
            return message

        return "Access"

    async def __choose_user_rules(
            self, user: User,
            calendar: CalendarModel
    ):
        """
        Choose user rules based on the calendar rules and user roles.

        :param user: User object in db.
        :param calendar: Calendar object in db.

        :return: Rules object.
        """
        reservation_service = await self.reservation_service_crud.get(
            calendar.reservation_service_id)

        if not user.active_member:
            return calendar.club_member_rules
        if reservation_service.alias in user.roles:
            return calendar.manager_rules
        return calendar.active_member_rules
