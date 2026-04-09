"""
Define an abstract base class AbstractEventService.

This class works with Event.
"""

import datetime as dt
import logging
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
from core.schemas.calendar import CalendarDetailWithCollisions
from core.schemas.event import EventLite
from core.schemas.google_calendar import EventEmail, EventTime, GoogleCalendarEventCreate
from crud import CRUDEvent, CRUDUser
from fastapi import BackgroundTasks, Depends
from integrations.google import GoogleCalendarService
from pytz import timezone
from services import CrudServiceBase
from services.calendar_services import CalendarService
from services.email_services import EmailService
from services.reservation_service_services import ReservationServiceService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


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
        background_tasks: BackgroundTasks,
        event_input: EventCreate,
        services: list[str],
        user: UserLite,
    ) -> Any:
        """
        Prepare for posting event in google calendar.

        :param background_tasks: BackgroundTasks used to run the email sending asynchronously.
        :param event_input: Input data for creating the event.
        :param services: UserLite services from IS.
        :param user: UserLite object in db.

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
        user: UserLite,
        background_tasks: BackgroundTasks,
        approve: bool = False,
        manager_notes: str = "-",
    ) -> EventLite | None:
        """
        Approve update a reservation time of the EventExtra in the database.

        :param id_: The id of the EventExtra.
        :param user: the UserSchema for control permissions of the event.
        :param background_tasks: BackgroundTasks for sending emails.
        :param approve: Whether to approve the update.
        :param manager_notes: Notes from the manager.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def update_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
        event_update: EventUpdate,
        background_tasks: BackgroundTasks,
        reason: str = "",
    ) -> EventLite | None:
        """
        Update a reservation of the EventExtra in the database.

        :param id_: The id of the EventExtra.
        :param event_update: EventUpdate SchemaLite for update.
        :param user: the UserSchema for control permissions of the event.
        :param background_tasks: BackgroundTasks for sending emails.
        :param reason: The reason for the update.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def request_update_reservation_time(
        self,
        id_: str,
        event_update: EventUpdateTime,
        user: UserLite,
        background_tasks: BackgroundTasks,
        reason: str = "",
    ) -> EventLite | None:
        """
        Update a reservation time of the EventExtra in the database.

        :param id_: The id of the EventExtra.
        :param event_update: EventUpdateTime SchemaLite for update.
        :param user: the UserSchema for control permissions of the event.
        :param background_tasks: BackgroundTasks for sending emails.
        :param reason: The reason for the update.

        :return: the updated EventExtra.
        """

    @abstractmethod
    async def cancel_event(
        self,
        id_: str,
        user: UserLite,
        background_tasks: BackgroundTasks,
        reason: str = "",
    ) -> EventLite | None:
        """
        Cancel an EventExtra in the database.

        :param id_: The id of the EventExtra.
        :param user: the UserSchema for control permissions of the event.
        :param background_tasks: BackgroundTasks for sending emails.
        :param reason: The reason for the cancellation.

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
    async def confirm_event(
        self,
        id_: str,
        user: UserLite,
        background_tasks: BackgroundTasks,
        manager_notes: str = "-",
    ) -> EventLite | None:
        """
        Confirm event.

        :param id_: The id of the event to confirm.
        :param user: the UserSchema for control permissions of the event.
        :param background_tasks: BackgroundTasks for sending emails.
        :param manager_notes: Notes from the manager.

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
        self.reservation_service_service = ReservationServiceService(db)
        self.calendar_service = CalendarService(db)
        self.user_crud = CRUDUser(db)
        self.google_calendar_service = GoogleCalendarService()
        self.email_service = EmailService()

    async def post_event(
        self,
        background_tasks: BackgroundTasks,
        event_input: EventCreate,
        services: list[str],
        user: UserLite,
    ) -> Any:
        calendar = await self.calendar_service.get_with_collisions(event_input.calendar_id)

        reservation_service = await self.reservation_service_service.get(
            calendar.reservation_service_id,
        )

        if not await self._control_collision(
            event_input,
            calendar,
        ):
            logger.warning("Collision detected for event by user %s", user.id)
            raise SoftValidationError("There's already a reservation for that time.")

        await self._control_conditions_and_permissions(
            user,
            services,
            event_input,
            calendar,
            reservation_service,
        )

        event_body: GoogleCalendarEventCreate = self._construct_event_body(
            calendar, event_input, user
        )

        if not event_body:
            logger.error("Failed to create event for user %s", user.id)
            raise BaseAppError(message="Could not create event.")

        return await self._process_event_approval(
            background_tasks,
            user,
            calendar,
            event_body,
            event_input,
            reservation_service,
        )

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
        calendar: CalendarDetail = await self.calendar_service.get(event.calendar_id)

        reservation_service: ReservationServiceDetail = await self.reservation_service_service.get(
            calendar.reservation_service_id
        )

        return reservation_service

    async def get_calendar_of_this_event(
        self,
        event: EventLite,
    ) -> CalendarDetail:
        calendar: CalendarDetail = await self.calendar_service.get(event.calendar_id)

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
        user: UserLite,
        background_tasks: BackgroundTasks,
        approve: bool = False,
        manager_notes: str = "-",
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

        event_update: EventUpdate = EventUpdate(
            event_state=EventState.CONFIRMED,
            requested_reservation_start=None,
            requested_reservation_end=None,
        )

        if not approve:
            logger.debug("Approving requested time change for event %s", id_)
            updated_event = await self.update(id_, event_update)

            await self.email_service.preparing_email(
                updated_event,
                self.email_service.create_email_meta(
                    "decline_update_reservation_time",
                    "Request Update Reservation Time Has Been Declined",
                    manager_notes,
                ),
                background_tasks,
            )
        else:
            logger.debug("Declining requested time change for event %s", id_)
            event_from_google_calendar = await self.google_calendar_service.get_event(
                event_to_update.calendar_id, id_
            )
            event_update.reservation_start = event_to_update.requested_reservation_start
            event_update.reservation_end = event_to_update.requested_reservation_end

            updated_event = await self.update(id_, event_update)

            prague = timezone("Europe/Prague")
            event_from_google_calendar.start.date_time = prague.localize(
                event_to_update.reservation_start,
            ).isoformat()
            event_from_google_calendar.end.date_time = prague.localize(
                event_to_update.reservation_end,
            ).isoformat()
            await self.email_service.preparing_email(
                updated_event,
                self.email_service.create_email_meta(
                    "approve_update_reservation_time",
                    "Request Update Reservation Time Has Been Approved",
                    manager_notes,
                ),
                background_tasks,
            )

            await self.google_calendar_service.update_event(
                updated_event.calendar_id, id_, event_from_google_calendar
            )

        logger.debug("Time change request processed for event %s: %s", id_, event_to_update)
        return updated_event

    async def update_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
        event_update: EventUpdate,
        background_tasks: BackgroundTasks,
        reason: str = "",
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

        event = await self.update(id_, event_update)

        event_to_update = await self.google_calendar_service.get_event(event.calendar_id, event.id)

        user = await self.user_crud.get(event.user_id)
        event_to_update.description = self._description_of_event(user, event)
        prague = timezone("Europe/Prague")
        event_to_update.start.date_time = prague.localize(event.reservation_start).isoformat()
        event_to_update.end.date_time = prague.localize(event.reservation_end).isoformat()

        await self.google_calendar_service.update_event(
            event.calendar_id, event.id, event_to_update
        )

        await self.email_service.preparing_email(
            event,
            self.email_service.create_email_meta(
                "update_reservation",
                "Update Reservation By Manager",
                reason,
            ),
            background_tasks,
        )

        logger.debug("Event updated: %s", event)
        return await self.update(id_, event_update)

    async def request_update_reservation_time(
        self,
        id_: str,
        event_update: EventUpdateTime,
        user: UserLite,
        background_tasks: BackgroundTasks,
        reason: str = "",
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

        event = await self.update(id_, event_update_time)

        await self.email_service.preparing_email(
            event,
            self.email_service.create_email_meta(
                "request_update_reservation_time",
                "Request Update Reservation Time",
                reason,
            ),
            background_tasks,
        )

        logger.debug("Time change request processed for event: %s", event)
        return event

    async def cancel_event(
        self,
        id_: str,
        user: UserLite,
        background_tasks: BackgroundTasks,
        reason: str = "",
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

        event = await self.update(id_, EventUpdate(event_state=EventState.CANCELED))

        await self.google_calendar_service.delete_event(event.calendar_id, event.id)

        if event.user_id == user.id:
            await self.email_service.preparing_email(
                event,
                self.email_service.create_email_meta("cancel_reservation", "Cancel Reservation"),
                background_tasks,
            )
        else:
            await self.email_service.preparing_email(
                event,
                self.email_service.create_email_meta(
                    "cancel_reservation_by_manager",
                    "Cancel Reservation by Manager",
                    reason,
                ),
                background_tasks,
            )

        logger.debug("Event cancelled: %s", event)

        return event

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

    async def confirm_event(
        self,
        id_: str,
        user: UserLite,
        background_tasks: BackgroundTasks,
        manager_notes: str = "-",
    ) -> EventLite | None:
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

        event = await self.update(id_, EventUpdate(event_state=EventState.CONFIRMED))

        calendar = await self.get_calendar_of_this_event(event)
        event_to_update = await self.google_calendar_service.get_event(event.calendar_id, event.id)

        event_to_update.summary = calendar.reservation_type

        await self.google_calendar_service.update_event(
            event.calendar_id, event.id, event_to_update
        )

        await self.email_service.preparing_email(
            event,
            self.email_service.create_email_meta(
                "approve_reservation",
                "Reservation Has Been Approved",
                manager_notes,
            ),
            background_tasks,
        )
        logger.debug("Reservation approved: %s", event)

        return event

    async def get_events_by_user_roles(
        self,
        user: UserLite,
        event_state: EventState | None = None,
        past: bool | None = None,
    ) -> list[EventDetail]:
        return await self.crud.get_events_by_aliases(user.roles, event_state, past)

    async def _control_collision(
        self,
        event_input: EventCreate,
        calendar: CalendarDetailWithCollisions,
    ) -> bool:
        """
        Check if there is already another reservation at that time.

        :param event_input: Input data for creating the event.
        :param calendar: CalendarDetail object in db.

        :return: Boolean indicating if here is already another reservation or not.
        """
        check_collision: list = []
        collisions: list = calendar.collision_ids
        collisions.append(calendar.id)
        for calendar_id in collisions:
            check_collision.extend(
                await self.google_calendar_service.fetch_events_in_time_range(
                    calendar_id,
                    event_input.start_datetime,
                    event_input.end_datetime,
                ),
            )

        return await self._check_collision_time(
            check_collision,
            event_input,
        )

    async def _control_conditions_and_permissions(
        self,
        user: UserLite,
        services: list[str],
        event_input: EventCreate,
        calendar: CalendarDetail,
        reservation_service: ReservationServiceDetail,
    ):
        """Check conditions and permissions for creating an event."""
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
        reservation_service = await self.reservation_service_service.get(
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
        return GoogleCalendarEventCreate(
            summary=calendar.reservation_type,
            description=self._description_of_event(user, event_input),
            start=EventTime(dateTime=start_time, timeZone="Europe/Prague"),
            end=EventTime(dateTime=end_time, timeZone="Europe/Prague"),
            attendees=[EventEmail(email=event_input.email)],
        )

    async def _process_event_approval(
        self,
        background_tasks: BackgroundTasks,
        user: UserLite,
        calendar: CalendarDetail,
        event_body: GoogleCalendarEventCreate,
        event_create: EventCreate,
        reservation_service: ReservationServiceDetail,
    ):
        """
        Approve or reject the event based on guest count and time rules.

        Creates the event in Google CalendarDetail and updates the local event state accordingly.
        Sends notification emails if the event is approved or not.

        :param background_tasks: BackgroundTasks used to run the email sending asynchronously.
        :param user: UserLite who make this request.
        :param calendar: CalendarDetail object in db.
        :param event_body: Google CalendarDetail-compatible event data.
        :param event_create: EventCreate schema.
        :param reservation_service: Reservation Service object in db.

        :return: Either a Google CalendarDetail event object if approved,
                 or a dictionary with a rejection message.
        """
        if event_create.guests > calendar.max_people:
            event_body.summary = f"Not approved - more than {calendar.max_people} people"
        elif not self._check_night_reservation(
            user
        ) and not self._control_available_reservation_time(
            event_create.start_datetime,
            event_create.end_datetime,
        ):
            event_body.summary = "Not approved - night time"
        else:
            event_google_calendar = await self.google_calendar_service.insert_event(
                calendar.id, event_body
            )
            event = await self.create_event(
                event_create,
                user,
                EventState.CONFIRMED,
                event_google_calendar.id,
            )
            event = await self.get(event.id)  # type: ignore[union-attr]
            await self.email_service.preparing_email(
                event,
                self.email_service.create_email_meta(
                    "confirm_reservation",
                    f"{reservation_service.name} Reservation Confirmation",
                ),
                background_tasks,
            )
            return event_google_calendar

        event_summary = event_body.summary
        event_google_calendar = await self.google_calendar_service.insert_event(
            event_create.calendar_id, event_body
        )
        event = await self.create_event(
            event_create,
            user,
            EventState.NOT_APPROVED,
            event_google_calendar.id,
        )
        event = await self.get(event.id)  # type: ignore[union-attr]
        if "night time" in event_summary.lower():
            await self.email_service.preparing_email(
                event,
                self.email_service.create_email_meta(
                    "not_approve_night_time_reservation", event_summary
                ),
                background_tasks,
            )
        return {"message": event_summary}

    @staticmethod
    async def _check_collision_time(
        check_collision,
        event_input: EventCreate,
    ) -> bool:
        """
        Check if there is already another reservation at that time.

        :param check_collision: Start time of the reservation.
        :param event_input: Input data for creating the event.

        :return: Boolean indicating if here is already another reservation or not.
        """
        if len(check_collision) == 0:
            return True

        if len(check_collision) > 1:
            return False

        start_date = dt.datetime.fromisoformat(str(event_input.start_datetime))
        end_date = dt.datetime.fromisoformat(str(event_input.end_datetime))
        start_date_event = dt.datetime.fromisoformat(
            str(check_collision[0]["start"]["dateTime"]),
        )
        end_date_event = dt.datetime.fromisoformat(
            str(check_collision[0]["end"]["dateTime"]),
        )

        return bool(
            end_date_event == start_date.astimezone(timezone("Europe/Prague"))
            or start_date_event == end_date.astimezone(timezone("Europe/Prague")),
        )

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
    def _check_night_reservation(user: UserLite) -> bool:
        """
        Control if user have permission for night reservation.

        :param user: UserLite object in db.

        :return: True if user can do night reservation and false otherwise.
        """
        return user.active_member

    @staticmethod
    def _control_available_reservation_time(start_datetime, end_datetime) -> bool:
        """
        Check if a user can reserve at night.

        :param start_datetime: Start time of the reservation.
        :param end_datetime: End time of the reservation.

        :return: Boolean indicating if a user can reserve at night or not.
        """
        start_time = start_datetime.time()
        end_time = end_datetime.time()

        start_res_time = dt.datetime.strptime("08:00:00", "%H:%M:%S").time()
        end_res_time = dt.datetime.strptime("22:00:00", "%H:%M:%S").time()

        return not (
            start_time < start_res_time or end_time < start_res_time or end_time > end_res_time
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
