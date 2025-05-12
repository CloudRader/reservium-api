"""
This module defines an abstract base class AbstractEventService that work with Event.
"""
import datetime as dt
from typing import Any, Annotated
from abc import ABC, abstractmethod

from models import CalendarModel, EventModel, EventState, ReservationServiceModel, UserModel
from services.utils import ready_event, first_standard_check, \
    dif_days_res, reservation_in_advance
from services import CrudServiceBase
from fastapi import Depends

from api import BaseAppException, PermissionDeniedException
from schemas import EventCreate, User, ServiceValidity, Calendar, \
    EventCreateToDb, EventUpdate, Event, EventUpdateTime, ReservationService, \
    EventWithExtraDetails
from db import db_session
from crud import CRUDReservationService, CRUDEvent, CRUDCalendar, CRUDUser
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
    async def post_event(self, event_input: EventCreate, services: list[ServiceValidity],
                         user: User, calendar: Calendar) -> Any:
        """
        Preparing for posting event in google calendar.
        :param event_input: Input data for creating the event.
        :param services: User services from IS.
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
    ) -> list[EventWithExtraDetails] | None:
        """
        Retrieves the Events instance by user id.

        :param user_id: user id of the events.

        :return: Events with user id equal
        to user id or empty list if no such events exists.
        """

    @abstractmethod
    async def get_by_event_state_by_reservation_service_alias(
            self, reservation_service_alias: str,
            event_state: EventState,
    ) -> list[EventWithExtraDetails]:
        """
        Retrieves the Events instance by reservation service alias.

        :param reservation_service_alias: reservation service alias of the events.
        :param event_state: event state of the event.

        :return: Events with reservation service alias equal
        to reservation service alias or empty list if no such events exists.
        """

    @abstractmethod
    async def get_reservation_service_of_this_event(
            self, event: Event,
    ) -> ReservationServiceModel:
        """
        Retrieve the ReservationService instance associated with this event.

        :param event: Event object in db.

        :return: ReservationService of this event.
        """

    @abstractmethod
    async def get_calendar_of_this_event(
            self, event: Event,
    ) -> CalendarModel:
        """
        Retrieve the Calendar instance associated with this event.

        :param event: Event object in db.

        :return: Calendar of this event.
        """

    @abstractmethod
    async def get_user_of_this_event(
            self, event: Event,
    ) -> UserModel:
        """
        Retrieve the User instance associated with this event.

        :param event: Event object in db.

        :return: User of this event.
        """

    @abstractmethod
    async def get_current_event_for_user(
            self, user_id: int
    ) -> EventModel | None:
        """
        Retrieves the current event for the given user where the current
        time is between start_datetime and end_datetime.

        :param user_id: ID of the user.

        :return: Matching Event or None.
        """

    @abstractmethod
    async def approve_update_reservation_time(self, uuid: str,
                                              event_update: EventUpdate,
                                              user: User) -> EventModel | None:
        """
        Approve update a reservation time of the Event in the database.

        :param uuid: The uuid of the Event.
        :param event_update: EventUpdate Schema for update.
        :param user: the UserSchema for control permissions of the event.

        :return: the updated Event.
        """

    @abstractmethod
    async def request_update_reservation_time(self, uuid: str,
                                              event_update: EventUpdateTime,
                                              user: User) -> EventModel | None:
        """
        Update a reservation time of the Event in the database.

        :param uuid: The uuid of the Event.
        :param event_update: EventUpdateTime Schema for update.
        :param user: the UserSchema for control permissions of the event.

        :return: the updated Event.
        """

    @abstractmethod
    async def cancel_event(
            self, uuid: str,
            user: User
    ) -> EventModel | None:
        """
        Cancel an Event in the database.

        :param uuid: The uuid of the Event.
        :param user: The user object used to control permissions
        for users authorized to perform this action.

        :return: the canceled Event.
        """

    @abstractmethod
    async def confirm_event(
            self, uuid: str | None,
            user: User
    ) -> EventModel | None:
        """
        Confirm event.

        :param uuid: The ID of the event to confirm.
        :param user: the UserSchema for control permissions users
        that can do this action.

        :return: the updated Event.
        """


class EventService(AbstractEventService):
    """
    Class EventService represent service that work with Event
    """

    def __init__(self, db: Annotated[
        AsyncSession, Depends(db_session.scoped_session_dependency)]):
        super().__init__(CRUDEvent(db))
        self.reservation_service_crud = CRUDReservationService(db)
        self.calendar_crud = CRUDCalendar(db)
        self.user_crud = CRUDUser(db)

    async def post_event(
            self, event_input: EventCreate,
            services: list[ServiceValidity], user: User,
            calendar: Calendar
    ) -> Any:
        if not calendar:
            return {"message": "Calendar with that type not exist!"}

        message = await self.__control_conditions_and_permissions(
            user, services, event_input, calendar)

        if message != "Access":
            return message

        return ready_event(calendar, event_input, user)

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
            additional_services=event_create.additional_services
        )
        return await self.crud.create(event_create_to_db)

    async def get_by_user_id(
            self, user_id: int,
    ) -> list[EventWithExtraDetails] | None:
        events = await self.crud.get_by_user_id(user_id)
        return await self.__add_extra_details_to_event(events)

    async def get_by_event_state_by_reservation_service_alias(
            self, reservation_service_alias: str,
            event_state: EventState,
    ) -> list[EventWithExtraDetails]:
        reservation_service = await self.reservation_service_crud.get_by_alias(
            reservation_service_alias)

        if not reservation_service:
            raise BaseAppException("A reservation service with this alias isn't exist.",
                                   status_code=404)

        events = await self.crud.get_by_event_state_by_reservation_service_id(
            reservation_service.id, event_state)

        return await self.__add_extra_details_to_event(events)

    async def get_reservation_service_of_this_event(
            self, event: Event,
    ) -> ReservationServiceModel:
        if not event:
            raise BaseAppException("This event does not exist in db.",
                                   status_code=404)

        calendar: Calendar = await self.calendar_crud.get(event.calendar_id)
        if not calendar:
            raise BaseAppException("A calendar of this event isn't exist.",
                                   status_code=404)

        reservation_service: ReservationService = await (self.reservation_service_crud.
                                                         get(calendar.reservation_service_id))
        if not reservation_service:
            raise BaseAppException("A reservation service of this event isn't exist.",
                                   status_code=404)

        return reservation_service

    async def get_calendar_of_this_event(
            self, event: Event,
    ) -> CalendarModel:
        if not event:
            raise BaseAppException("This event does not exist in db.",
                                   status_code=404)

        calendar: Calendar = await self.calendar_crud.get(event.calendar_id)
        if not calendar:
            raise BaseAppException("A calendar of this event isn't exist.",
                                   status_code=404)

        return calendar

    async def get_user_of_this_event(
            self, event: Event,
    ) -> UserModel:
        if not event:
            raise BaseAppException("This event does not exist in db.",
                                   status_code=404)

        user = await self.user_crud.get(event.user_id)

        if not user:
            raise BaseAppException("A user of this event isn't exist.",
                                   status_code=404)

        return user

    async def get_current_event_for_user(
            self, user_id: int
    ) -> EventModel | None:
        return await self.crud.get_current_event_for_user(user_id)

    async def approve_update_reservation_time(self, uuid: str,
                                              event_update: EventUpdate,
                                              user: User) -> EventModel | None:
        event_to_update = await self.get(uuid)

        if event_to_update is None:
            return None

        if event_to_update.event_state == EventState.CANCELED:
            raise BaseAppException("You can't change canceled reservation.")

        reservation_service = await self.get_reservation_service_of_this_event(event_to_update)

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to update this event."
            )

        return await self.update(uuid, event_update)

    async def request_update_reservation_time(self, uuid: str,
                                              event_update: EventUpdateTime,
                                              user: User) -> EventModel | None:
        event_to_update = await self.get(uuid)

        if not event_to_update:
            return None

        if event_to_update.start_datetime < dt.datetime.now():
            raise BaseAppException("You cannot change the reservation time after it has started.")

        if event_to_update.event_state == EventState.CANCELED:
            raise BaseAppException("You can't change canceled reservation.")

        if event_to_update.event_state == EventState.UPDATE_REQUESTED:
            raise BaseAppException("You can't change reservation in state update requested.")

        event_update_time = EventUpdate(
            start_datetime=event_update.start_datetime,
            end_datetime=event_update.end_datetime,
            event_state=EventState.UPDATE_REQUESTED
        )
        return await self.update(uuid, event_update_time)

    async def cancel_event(
            self, uuid: str,
            user: User
    ) -> EventModel | None:
        event: Event = await self.get(uuid)
        if not event:
            return None

        if event.event_state == EventState.CANCELED:
            raise BaseAppException("You can't cancel canceled reservation.")

        if event.start_datetime < dt.datetime.now():
            raise BaseAppException("You cannot cancel the reservation after it has started.")

        reservation_service = await self.get_reservation_service_of_this_event(event)

        if event.user_id != user.id:
            if reservation_service.alias not in user.roles:
                raise PermissionDeniedException("You do not have permission to cancel a "
                                                "reservation made by another user.")

        updated_event = EventUpdate(
            event_state=EventState.CANCELED
        )

        return await self.update(uuid, updated_event)

    async def confirm_event(
            self, uuid: str | None,
            user: User
    ) -> EventModel | None:
        event: Event = await self.get(uuid)
        if not event:
            return None

        if event.event_state != EventState.NOT_APPROVED:
            raise BaseAppException("You cannot approve a reservation that is not in the "
                                   "'not approved' state.")

        reservation_service = await self.get_reservation_service_of_this_event(event)

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to approve this reservation."
            )

        return await self.crud.confirm_event(uuid)

    async def __control_conditions_and_permissions(
            self, user: User,
            services: list[ServiceValidity],
            event_input: EventCreate,
            calendar: CalendarModel
    ) -> str | dict:
        """
        Check conditions and permissions for creating an event.

        :param user: User object in db.
        :param services: User services from IS.
        :param event_input: Input data for creating the event.
        :param calendar: Calendar object in db.
        ReservationService objects in db.

        :return: Message indicating whether access is granted or denied.
        """
        reservation_service = await self.reservation_service_crud.get(
            calendar.reservation_service_id)

        # Check of the membership
        standard_message = first_standard_check(services, reservation_service,
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

    async def __add_extra_details_to_event(
            self, events: list[Event]
    ) -> list[EventWithExtraDetails]:
        """
        Enrich a list of Event objects data.

        :param events: A list of Event objects to be enriched.

        :return: A list of EventWithExtraDetails, containing
        the original event and related metadata.
        """
        result = []

        for event in events:
            calendar = await self.get_calendar_of_this_event(event)
            user = await self.get_user_of_this_event(event)
            reservation_service = await  self.get_reservation_service_of_this_event(event)

            event_with_details = EventWithExtraDetails(
                event=event,
                reservation_type=calendar.reservation_type,
                user_name=user.full_name,
                reservation_service_name=reservation_service.name
            )
            result.append(event_with_details)

        return result
