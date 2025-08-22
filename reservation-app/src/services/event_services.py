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
    ServiceValidity,
    UserLite,
)
from core.schemas.event import EventLite
from crud import CRUDCalendar, CRUDEvent, CRUDReservationService, CRUDUser
from fastapi import Depends
from pytz import timezone
from services import CrudServiceBase
from services.utils import (
    dif_days_res,
    first_standard_check,
    reservation_in_advance,
)
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
        services: list[ServiceValidity],
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
        event_id: str,
    ) -> EventDetail | None:
        """
        Create an EventExtra in the database.

        :param event_create: EventCreate SchemaLite for create.
        :param user: the UserSchema for control permissions of the reservation service.
        :param event_state: State of the event.
        :param event_id: EventExtra id in google calendar.

        :return: the created EventExtra.
        """

    @abstractmethod
    async def get_reservation_service_of_this_event(
        self,
        event: EventDetail,
    ) -> ReservationServiceDetail:
        """
        Retrieve the ReservationServiceDetail instance associated with this event.

        :param event: EventExtra object in db.

        :return: ReservationServiceDetail of this event.
        """

    @abstractmethod
    async def get_calendar_of_this_event(
        self,
        event: EventDetail,
    ) -> CalendarDetail:
        """
        Retrieve the CalendarDetail instance associated with this event.

        :param event: EventExtra object in db.

        :return: CalendarDetail of this event.
        """

    @abstractmethod
    async def get_user_of_this_event(
        self,
        event: EventDetail,
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
        uuid: str,
        event_update: EventUpdate,
        user: UserLite,
    ) -> EventDetail | None:
        """
        Approve update a reservation time of the EventExtra in the database.

        :param uuid: The uuid of the EventExtra.
        :param event_update: EventUpdate SchemaLite for update.
        :param user: the UserSchema for control permissions of the event.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def update_with_permission_checks(
        self,
        uuid: str,
        event_update: EventUpdate,
        user: UserLite,
    ) -> EventDetail | None:
        """
        Update a reservation of the EventExtra in the database.

        :param uuid: The id of the EventExtra.
        :param event_update: EventUpdate SchemaLite for update.
        :param user: the UserSchema for control permissions of the event.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def request_update_reservation_time(
        self,
        uuid: str,
        event_update: EventUpdateTime,
        user: UserLite,
    ) -> EventDetail | None:
        """
        Update a reservation time of the EventExtra in the database.

        :param uuid: The uuid of the EventExtra.
        :param event_update: EventUpdateTime SchemaLite for update.
        :param user: the UserSchema for control permissions of the event.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def cancel_event(
        self,
        uuid: str,
        user: UserLite,
    ) -> EventDetail | None:
        """
        Cancel an EventExtra in the database.

        :param uuid: The uuid of the EventExtra.
        :param user: The user object used to control permissions
        for users authorized to perform this action.

        :return: the canceled EventExtra.
        """

    @abstractmethod
    async def delete_with_permission_checks(
        self,
        uuid: str,
        user: UserLite,
    ) -> ReservationServiceDetail | None:
        """
        Delete an EventExtra in the database.

        :param uuid: The uuid of the EventExtra.
        :param user: the UserSchema for control permissions of the event.

        :return: the deleted EventExtra.
        """

    @abstractmethod
    async def confirm_event(self, uuid: str | None, user: UserLite) -> EventDetail | None:
        """
        Confirm event.

        :param uuid: The ID of the event to confirm.
        :param user: the UserSchema for control permissions users
        that can do this action.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def get_events_by_user_roles(
        self,
        user: UserLite,
        event_state: EventState | None = None,
    ) -> list[EventDetail]:
        """
        Retrieve events for the given user roles.

        :param user: the UserSchema for control permissions users
        :param event_state: EventExtra state of the event.

        :return: Matching list of EventDetail.
        """


class EventService(AbstractEventService):
    """Class EventService represent service that work with EventExtra."""

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(db_session.scoped_session_dependency)],
    ):
        super().__init__(CRUDEvent(db))
        self.reservation_service_crud = CRUDReservationService(db)
        self.calendar_crud = CRUDCalendar(db)
        self.user_crud = CRUDUser(db)

    async def post_event(
        self,
        event_input: EventCreate,
        services: list[ServiceValidity],
        user: UserLite,
        calendar: CalendarDetail,
    ) -> Any:
        await self.__control_conditions_and_permissions(
            user,
            services,
            event_input,
            calendar,
        )

        return self.construct_event_body(calendar, event_input, user)

    async def create_event(
        self,
        event_create: EventCreate,
        user: UserLite,
        event_state: EventState,
        event_id: str,
    ) -> EventLite | None:
        event_create_to_db = EventLite(
            id=event_id,
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
        if not event:
            raise BaseAppError("This event does not exist in db.", status_code=404)

        calendar: CalendarDetail = await self.calendar_crud.get(event.calendar_id)
        if not calendar:
            raise BaseAppError("A calendar of this event isn't exist.", status_code=404)

        reservation_service: ReservationServiceDetail = await self.reservation_service_crud.get(
            calendar.reservation_service_id
        )
        if not reservation_service:
            raise BaseAppError(
                "A reservation service of this event isn't exist.",
                status_code=404,
            )

        return reservation_service

    async def get_calendar_of_this_event(
        self,
        event: EventLite,
    ) -> CalendarDetail:
        if not event:
            raise BaseAppError("This event does not exist in db.", status_code=404)

        calendar: CalendarDetail = await self.calendar_crud.get(event.calendar_id)
        if not calendar:
            raise BaseAppError("A calendar of this event isn't exist.", status_code=404)

        return calendar

    async def get_user_of_this_event(
        self,
        event: EventLite,
    ) -> UserLite:
        if not event:
            raise BaseAppError("This event does not exist in db.", status_code=404)

        user = await self.user_crud.get(event.user_id)

        if not user:
            raise BaseAppError("A user of this event isn't exist.", status_code=404)

        return user

    async def get_current_event_for_user(self, user_id: int) -> EventDetail | None:
        return await self.crud.get_current_event_for_user(user_id)

    async def approve_update_reservation_time(
        self,
        uuid: str,
        event_update: EventUpdate,
        user: UserLite,
    ) -> EventLite | None:
        event_to_update = await self.get(uuid)

        if event_to_update is None:
            return None

        if event_to_update.event_state == EventState.CANCELED:
            raise BaseAppError("You can't change canceled reservation.")

        reservation_service = await self.get_reservation_service_of_this_event(
            event_to_update,
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to update this event.",
            )

        return await self.update(uuid, event_update)

    async def update_with_permission_checks(
        self,
        uuid: str,
        event_update: EventUpdate,
        user: UserLite,
    ) -> EventDetail | None:
        event_to_update = await self.get(uuid)

        if event_to_update is None:
            return None

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

        return await self.update(uuid, event_update)

    async def request_update_reservation_time(
        self,
        uuid: str,
        event_update: EventUpdateTime,
        user: UserLite,
    ) -> EventDetail | None:
        event_to_update = await self.get(uuid)

        if not event_to_update:
            return None

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
        return await self.update(uuid, event_update_time)

    async def cancel_event(
        self,
        uuid: str,
        user: UserLite,
    ) -> EventLite | None:
        event: EventLite = await self.get(uuid)
        if not event:
            return None

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

        return await self.update(uuid, updated_event)

    async def delete_with_permission_checks(
        self,
        uuid: str,
        user: UserLite,
    ) -> ReservationServiceDetail | None:
        event = await self.crud.get(uuid, True)

        if event is None:
            return None

        reservation_service = await self.get_reservation_service_of_this_event(event)

        if event.event_state != EventState.CANCELED:
            raise BaseAppError("You can't deleted not canceled reservation.")

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to delete event.",
            )

        return await self.crud.remove(uuid)

    async def confirm_event(self, uuid: str | None, user: UserLite) -> EventDetail | None:
        event: EventLite = await self.get(uuid)
        if not event:
            return None

        if event.event_state != EventState.NOT_APPROVED:
            raise BaseAppError(
                "You cannot approve a reservation that is not in the 'not approved' state.",
            )

        reservation_service = await self.get_reservation_service_of_this_event(event)

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to approve this reservation.",
            )

        return await self.crud.confirm_event(uuid)

    async def __control_conditions_and_permissions(
        self,
        user: UserLite,
        services: list[ServiceValidity],
        event_input: EventCreate,
        calendar: CalendarDetail,
    ):
        """
        Check conditions and permissions for creating an event.

        :param user: UserLite object in db.
        :param services: UserLite services from IS.
        :param event_input: Input data for creating the event.
        :param calendar: CalendarDetail object in db.

        :return: Message indicating whether access is granted or denied.
        """
        reservation_service = await self.reservation_service_crud.get(
            calendar.reservation_service_id,
        )

        # Check of the membership
        first_standard_check(
            services,
            reservation_service,
            event_input.start_datetime,
            event_input.end_datetime,
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
        user_rules = await self.__choose_user_rules(user, calendar)

        # Reservation no more than 24 hours
        if not dif_days_res(
            event_input.start_datetime,
            event_input.end_datetime,
            user_rules,
        ):
            raise SoftValidationError(
                f"Reservation exceeds the allowed maximum of "
                f"{user_rules.max_reservation_hours} hours."
            )

        # Check reservation in advance and prior
        reservation_in_advance(event_input.start_datetime, user_rules)

    async def __choose_user_rules(self, user: UserLite, calendar: CalendarDetail):
        """
        Choose user rules based on the calendar rules and user roles.

        :param user: UserLite object in db.
        :param calendar: CalendarDetail object in db.

        :return: Rules object.
        """
        reservation_service = await self.reservation_service_crud.get(
            calendar.reservation_service_id,
        )

        if not user.active_member:
            return calendar.club_member_rules
        if reservation_service.alias in user.roles:
            return calendar.manager_rules
        return calendar.active_member_rules

    @staticmethod
    def description_of_event(
        user: UserLite,
        event_input: EventCreate | EventDetail,
    ):
        """
        Describe the event.

        :param user: UserLite object in db.
        :param event_input: Input data for creating the event.

        :return: String of the description.
        """
        formatted_services: str = "-"
        if event_input.additional_services:
            formatted_services = ", ".join(event_input.additional_services)
        return (
            f"Name: {user.full_name}\n"
            f"Room: {user.room_number}\n"
            f"Participants: {event_input.guests}\n"
            f"Purpose: {event_input.purpose}\n"
            f"\n"
            f"Additionals: {formatted_services}\n"
        )

    def construct_event_body(
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
            "description": self.description_of_event(user, event_input),
            "start": {"dateTime": start_time, "timeZone": "Europe/Prague"},
            "end": {"dateTime": end_time, "timeZone": "Europe/Prague"},
            "attendees": [
                {"email": event_input.email},
            ],
        }

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

    async def get_events_by_user_roles(
        self,
        user: UserLite,
        event_state: EventState | None = None,
    ) -> list[EventDetail]:
        return await self.crud.get_events_by_aliases(user.roles, event_state)
