"""
Define an abstract base class AbstractEventService.

This class works with Event.
"""

import datetime as dt
from abc import ABC, abstractmethod
from typing import Annotated, Any

from core import db_session
from core.application.exceptions import (
    BaseAppError,
    Entity,
    PermissionDeniedError,
    SoftValidationError,
)
from core.models import EventState
from core.schemas import (
    CalendarDetail,
    EventCreate,
    EventDetail,
    EventUpdate,
    EventUpdateTime,
    ReservationServiceDetail,
    Rules,
    UserLite,
)
from core.schemas.event import EventLite
from crud import CRUDCalendar, CRUDEvent, CRUDReservationService, CRUDUser
from fastapi import Depends
from pytz import timezone
from services import CrudServiceBase
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractEventService(
    CrudServiceBase[
        EventLite,
        EventDetail,
        CRUDEvent,
        EventLite,
        EventUpdate,
    ],
    ABC,
):
    """Abstract class defines the interface for an event service."""

    @abstractmethod
    async def post_event(
        self,
        event_input: EventCreate,
        services: list[str],
        user: UserLite,
        calendar: CalendarDetail,
    ) -> Any:
        """
        Prepare for posting event in google calendar.

        :param event_input: Input data for creating the event.
        :param services: UserLite services from IS.
        :param user: UserLite object in db.
        :param calendar: CalendarDetail object in db.

        :returns EventExtra json object: the created event or exception otherwise.
        """

    @abstractmethod
    async def create_event(
        self,
        event_create: EventCreate,
        user: UserLite,
        event_state: EventState,
        id_: str,
    ) -> EventDetail | None:
        """
        Create an EventExtra in the database.

        :param event_create: EventCreate SchemaLite for create.
        :param user: the UserSchema for control permissions of the reservation service.
        :param event_state: State of the event.
        :param id_: EventExtra id in google calendar.

        :return: the created EventExtra.
        """

    @abstractmethod
    async def get_reservation_service_of_this_event(
        self,
        event: EventLite,
    ) -> ReservationServiceDetail:
        """
        Retrieve the ReservationServiceDetail instance associated with this event.

        :param event: EventExtra object in db.

        :return: ReservationServiceDetail of this event.
        """

    @abstractmethod
    async def get_calendar_of_this_event(
        self,
        event: EventLite,
    ) -> CalendarDetail:
        """
        Retrieve the CalendarDetail instance associated with this event.

        :param event: EventExtra object in db.

        :return: CalendarDetail of this event.
        """

    @abstractmethod
    async def get_user_of_this_event(
        self,
        event: EventLite,
    ) -> UserLite:
        """
        Retrieve the UserLite instance associated with this event.

        :param event: EventExtra object in db.

        :return: UserLite of this event.
        """

    @abstractmethod
    async def get_current_event_for_user(self, user_id: int) -> EventDetail | None:
        """
        Retrieve the current event for the given user.

        Current time is between start_datetime and end_datetime.

        :param user_id: ID of the user.

        :return: Matching EventExtra or None.
        """

    @abstractmethod
    async def approve_update_reservation_time(
        self,
        id_: str,
        event_update: EventUpdate,
        user: UserLite,
    ) -> EventLite | None:
        """
        Approve update a reservation time of the EventExtra in the database.

        :param id_: The id of the EventExtra.
        :param event_update: EventUpdate SchemaLite for update.
        :param user: the UserSchema for control permissions of the event.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def update_with_permission_checks(
        self,
        id_: str,
        event_update: EventUpdate,
        user: UserLite,
    ) -> EventLite | None:
        """
        Update a reservation of the EventExtra in the database.

        :param id_: The id of the EventExtra.
        :param event_update: EventUpdate SchemaLite for update.
        :param user: the UserSchema for control permissions of the event.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def request_update_reservation_time(
        self,
        id_: str,
        event_update: EventUpdateTime,
        user: UserLite,
    ) -> EventLite | None:
        """
        Update a reservation time of the EventExtra in the database.

        :param id_: The id of the EventExtra.
        :param event_update: EventUpdateTime SchemaLite for update.
        :param user: the UserSchema for control permissions of the event.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def cancel_event(
        self,
        id_: str,
        user: UserLite,
    ) -> EventLite | None:
        """
        Cancel an EventExtra in the database.

        :param id_: The id of the EventExtra.
        :param user: The user object used to control permissions
        for users authorized to perform this action.

        :return: the canceled EventExtra.
        """

    @abstractmethod
    async def delete_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
    ) -> EventLite | None:
        """
        Delete an EventExtra in the database.

        :param id_: The id of the EventExtra.
        :param user: the UserSchema for control permissions of the event.

        :return: the deleted EventExtra.
        """

    @abstractmethod
    async def confirm_event(self, id_: str | None, user: UserLite) -> EventLite | None:
        """
        Confirm event.

        :param id_: The id of the event to confirm.
        :param user: the UserSchema for control permissions users
        that can do this action.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def get_events_by_user_roles(
        self,
        user: UserLite,
        event_state: EventState | None = None,
        past: bool | None = None,
    ) -> list[EventDetail]:
        """
        Retrieve events for the given user roles.

        :param user: the UserSchema for control permissions users
        :param event_state: EventExtra state of the event.
        :param past: Filter for event time. `True` for past events, `False` for future events.
            `None` to fetch all events (no time filtering).

        :return: Matching list of EventDetail.
        """


class EventService(AbstractEventService):
    """Class EventService represent service that work with EventExtra."""

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(db_session.scoped_session_dependency)],
    ):
        super().__init__(CRUDEvent(db), Entity.EVENT)
        self.reservation_service_crud = CRUDReservationService(db)
        self.calendar_crud = CRUDCalendar(db)
        self.user_crud = CRUDUser(db)

    async def post_event(
        self,
        event_input: EventCreate,
        services: list[str],
        user: UserLite,
        calendar: CalendarDetail,
    ) -> Any:
        await self._control_conditions_and_permissions(
            user,
            services,
            event_input,
            calendar,
        )

        return self._construct_event_body(calendar, event_input, user)

    async def create_event(
        self,
        event_create: EventCreate,
        user: UserLite,
        event_state: EventState,
        id_: str,
    ) -> EventLite | None:
        event_create_to_db = EventLite(
            id=id_,
            reservation_start=event_create.start_datetime,
            reservation_end=event_create.end_datetime,
            purpose=event_create.purpose,
            guests=event_create.guests,
            email=event_create.email,
            event_state=event_state,
            user_id=user.id,
            calendar_id=event_create.calendar_id,
            additional_services=event_create.additional_services,
        )
        return await self.crud.create(event_create_to_db)

    async def get_reservation_service_of_this_event(
        self,
        event: EventLite,
    ) -> ReservationServiceDetail:
        calendar: CalendarDetail = await self.calendar_crud.get(event.calendar_id)

        reservation_service: ReservationServiceDetail = await self.reservation_service_crud.get(
            calendar.reservation_service_id
        )

        return reservation_service

    async def get_calendar_of_this_event(
        self,
        event: EventLite,
    ) -> CalendarDetail:
        calendar: CalendarDetail = await self.calendar_crud.get(event.calendar_id)

        return calendar

    async def get_user_of_this_event(
        self,
        event: EventLite,
    ) -> UserLite:
        return await self.user_crud.get(event.user_id)

    async def get_current_event_for_user(self, user_id: int) -> EventDetail | None:
        return await self.crud.get_current_event_for_user(user_id)

    async def approve_update_reservation_time(
        self,
        id_: str,
        event_update: EventUpdate,
        user: UserLite,
    ) -> EventLite | None:
        event_to_update = await self.get(id_)

        if event_to_update.event_state == EventState.CANCELED:
            raise BaseAppError("You can't change canceled reservation.")

        reservation_service = await self.get_reservation_service_of_this_event(
            event_to_update,
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to update this event.",
            )

        return await self.update(id_, event_update)

    async def update_with_permission_checks(
        self,
        id_: str,
        event_update: EventUpdate,
        user: UserLite,
    ) -> EventLite | None:
        event_to_update = await self.get(id_)

        reservation_service = await self.get_reservation_service_of_this_event(event_to_update)

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to update event.",
            )

        event_update = self.datetime_for_update(event_to_update, event_update)
        if event_update.reservation_start < dt.datetime.now():
            raise SoftValidationError(
                "You can't change a reservation start time before the present time!"
            )

        if event_update.reservation_end < event_update.reservation_start:
            raise SoftValidationError("The end of a reservation cannot be before its beginning!")

        return await self.update(id_, event_update)

    async def request_update_reservation_time(
        self,
        id_: str,
        event_update: EventUpdateTime,
        user: UserLite,
    ) -> EventLite | None:
        event_to_update = await self.get(id_)

        if event_to_update.user_id != user.id:
            raise PermissionDeniedError(
                "You do not have permission to request change a reservation made by another user.",
            )

        if event_to_update.reservation_start < dt.datetime.now():
            raise BaseAppError(
                "You cannot change the reservation time after it has started.",
            )

        if event_to_update.event_state == EventState.CANCELED:
            raise BaseAppError("You can't change canceled reservation.")

        if event_to_update.event_state == EventState.UPDATE_REQUESTED:
            raise BaseAppError(
                "You can't change reservation in state update requested.",
            )

        event_update_time = EventUpdate(
            requested_reservation_start=event_update.requested_reservation_start,
            requested_reservation_end=event_update.requested_reservation_end,
            event_state=EventState.UPDATE_REQUESTED,
        )
        return await self.update(id_, event_update_time)

    async def cancel_event(
        self,
        id_: str,
        user: UserLite,
    ) -> EventLite | None:
        event = await self.get(id_)

        if event.event_state == EventState.CANCELED:
            raise BaseAppError("You can't cancel canceled reservation.")

        if event.reservation_end < dt.datetime.now():
            raise BaseAppError(
                "You cannot cancel the reservation after it has ended.",
            )

        reservation_service = await self.get_reservation_service_of_this_event(event)

        if event.user_id != user.id and reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                "You do not have permission to cancel a reservation made by another user.",
            )

        updated_event = EventUpdate(event_state=EventState.CANCELED)

        return await self.update(id_, updated_event)

    async def delete_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
    ) -> EventLite | None:
        event = await self.crud.get(id_, True)

        reservation_service = await self.get_reservation_service_of_this_event(event)

        if event.event_state != EventState.CANCELED:
            raise BaseAppError("You can't deleted not canceled reservation.")

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to delete event.",
            )

        return await self.crud.remove(id_)

    async def confirm_event(self, id_: str | None, user: UserLite) -> EventLite | None:
        event = await self.get(id_)

        if event.event_state != EventState.NOT_APPROVED:
            raise BaseAppError(
                "You cannot approve a reservation that is not in the 'not approved' state.",
            )

        reservation_service = await self.get_reservation_service_of_this_event(event)

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to approve this reservation.",
            )

        return await self.crud.confirm_event(id_)

    async def get_events_by_user_roles(
        self,
        user: UserLite,
        event_state: EventState | None = None,
        past: bool | None = None,
    ) -> list[EventDetail]:
        return await self.crud.get_events_by_aliases(user.roles, event_state, past)

    async def _control_conditions_and_permissions(
        self,
        user: UserLite,
        services: list[str],
        event_input: EventCreate,
        calendar: CalendarDetail,
    ):
        """Check conditions and permissions for creating an event."""
        reservation_service = await self.reservation_service_crud.get(
            calendar.reservation_service_id,
        )

        self._first_standard_check(
            services,
            reservation_service,
            event_input.start_datetime,
        )

        if (
            not calendar.more_than_max_people_with_permission
            and event_input.guests > calendar.max_people
        ):
            raise SoftValidationError(
                f"You can't reserve this type of "
                f"reservation for more than {calendar.max_people} people!"
            )

        # Choose user rules
        user_rules = await self._choose_user_rules(user, calendar)

        self._check_max_user_reservation_hours(
            event_input.start_datetime, event_input.end_datetime, user_rules
        )

        # Check reservation in advance and prior
        self._reservation_in_advance(event_input.start_datetime, user_rules)

    async def _choose_user_rules(self, user: UserLite, calendar: CalendarDetail):
        """Choose user rules based on the calendar rules and user roles."""
        reservation_service = await self.reservation_service_crud.get(
            calendar.reservation_service_id,
        )

        if not user.active_member:
            return calendar.club_member_rules
        if reservation_service.alias in user.roles:
            return calendar.manager_rules
        return calendar.active_member_rules

    def _first_standard_check(
        self,
        services: list[str],
        reservation_service: ReservationServiceDetail,
        start_time,
    ):
        """
        Check if the user is reserving the service user has.

        And that user can't reserve before current date.
        """
        # Check of the membership
        if not self._service_availability_check(services, reservation_service.alias):
            raise SoftValidationError(f"You don't have {reservation_service.alias} service!")

        # Check error reservation
        if start_time < dt.datetime.now():
            raise SoftValidationError("You can't make a reservation before the present time!")

    def _reservation_in_advance(self, start_time, user_rules):
        """Check if the reservation is made within the specified advance and prior time."""
        # Reservation in advance
        if not self._control_res_in_advance_or_prior(start_time, user_rules, True):
            raise SoftValidationError(
                f"You have to make reservations "
                f"{user_rules.in_advance_hours} hours and "
                f"{user_rules.in_advance_minutes} minutes in advance!"
            )

        # Reservation prior than
        if not self._control_res_in_advance_or_prior(start_time, user_rules, False):
            raise SoftValidationError(
                f"You can't make reservations earlier than {user_rules.in_prior_days} "
                f"days in advance!"
            )

    def _construct_event_body(
        self,
        calendar: CalendarDetail,
        event_input: EventCreate,
        user: UserLite,
    ):
        """
        Construct the body of the event.

        :param calendar: CalendarDetail object in db.
        :param event_input: Input data for creating the event.
        :param user: UserLite object in db.

        :return: Dict body of the event.
        """
        prague = timezone("Europe/Prague")

        start_time = prague.localize(event_input.start_datetime).isoformat()
        end_time = prague.localize(event_input.end_datetime).isoformat()
        return {
            "summary": calendar.reservation_type,
            "description": self._description_of_event(user, event_input),
            "start": {"dateTime": start_time, "timeZone": "Europe/Prague"},
            "end": {"dateTime": end_time, "timeZone": "Europe/Prague"},
            "attendees": [
                {"email": event_input.email},
            ],
        }

    @staticmethod
    def _service_availability_check(services: list[str], service_alias) -> bool:
        """Check if the user is reserving the service user has."""
        return any(service == service_alias for service in services)

    @staticmethod
    def _check_max_user_reservation_hours(start_datetime, end_datetime, user_rules: Rules):
        """Check if the reservation duration is less than user can reserve."""
        duration = end_datetime - start_datetime
        if duration >= dt.timedelta(hours=user_rules.max_reservation_hours):
            raise SoftValidationError(
                f"Reservation exceeds the allowed maximum of "
                f"{user_rules.max_reservation_hours} hours."
            )

    @staticmethod
    def _control_res_in_advance_or_prior(
        start_time,
        user_rules: Rules,
        in_advance: bool,
    ) -> bool:
        """Check if the reservation is made within the specified advance or prior time."""
        current_time = dt.datetime.now()

        time_difference = abs(start_time - current_time)

        if in_advance:
            if time_difference < dt.timedelta(
                minutes=user_rules.in_advance_minutes,
                hours=user_rules.in_advance_hours,
            ):
                return False
        elif time_difference > dt.timedelta(days=user_rules.in_prior_days):
            return False
        return True

    @staticmethod
    def _description_of_event(
        user: UserLite,
        event_input: EventCreate | EventLite,
    ):
        """Describe the event in google calendar."""
        formatted_services: str = "-"
        if event_input.additional_services:
            formatted_services = ", ".join(event_input.additional_services)
        return (
            f"Name: {user.full_name}\n"
            f"Participants: {event_input.guests}\n"
            f"Purpose: {event_input.purpose}\n"
            f"\n"
            f"Additionals: {formatted_services}\n"
        )

    @staticmethod
    def datetime_for_update(
        event: EventLite,
        event_update: EventUpdate,
    ):
        """
        Ensure reservation datetimes are set during update.

        If the update payload does not include `reservation_start` or `reservation_end`,
        these values are copied from the existing event to guarantee valid
        collision checks and prevent partial/invalid time updates.
        """
        if not event_update.reservation_start:
            event_update.reservation_start = event.reservation_start
        if not event_update.reservation_end:
            event_update.reservation_end = event.reservation_end

        return event_update
