"""API controllers for events."""

import logging
from typing import Annotated, Any

from api import (
    get_current_user,
)
from api.api_base import BaseCRUDRouter
from api.dependencies import http_bearer
from api.utils import control_collision, process_event_approval
from api.v2.emails import create_email_meta, preparing_email
from core.application.exceptions import (
    ERROR_RESPONSES,
    BaseAppError,
    Entity,
    EntityNotFoundError,
    SoftValidationError,
)
from core.models import EventState
from core.schemas import (
    EventCreate,
    EventDetail,
    EventLite,
    EventUpdate,
    EventUpdateTime,
    UserLite,
)
from core.schemas.google_calendar import GoogleCalendarEventCreate
from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from integrations.google import GoogleCalendarService
from integrations.keycloak import KeycloakAuthService
from pytz import timezone
from services import CalendarService, EventService

logger = logging.getLogger(__name__)

router = APIRouter()


class EventRouter(
    BaseCRUDRouter[
        EventCreate,
        EventUpdate,
        EventLite,
        EventDetail,
        EventService,
    ]
):
    """
    API router for managing Events.

    This class extends `BaseCRUDRouter` to automatically register standard
    CRUD routes for the `Events` entity and adds custom endpoints
    specific to Events.
    """

    def __init__(self):  # noqa: C901
        super().__init__(
            router=router,
            service_dep=EventService,
            schema_create=EventCreate,
            schema_update=EventUpdate,
            schema_lite=EventLite,
            schema_detail=EventDetail,
            entity_name=Entity.EVENT,
            enable_create=False,
            enable_create_multiple=False,
            enable_update=False,
            enable_restore=False,
            enable_delete=False,
        )

        @router.get(
            "/get-by-user-roles",
            response_model=list[EventDetail],
            status_code=status.HTTP_200_OK,
        )
        async def get_by_user_roles(
            service: Annotated[EventService, Depends(EventService)],
            user: Annotated[UserLite, Depends(get_current_user)],
            event_state: Annotated[EventState | None, Query()] = None,
        ) -> Any:
            """
            Get all events.

            :param service: EventExtra Service.
            :param user: UserLite who make this request.
            :param event_state: event state of the event.

            :return: List of EventDetail objects.
            """
            logger.info("User %s fetching events by roles (state=%s)", user.id, event_state)
            events = await service.get_events_by_user_roles(user, event_state)
            logger.debug("Fetched %d events for user %s", len(events), user.id)
            return events

        self.register_routes()

        @router.post(
            "/",
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_201_CREATED,
        )
        async def create(
            service: Annotated[EventService, Depends(EventService)],
            calendar_service: Annotated[CalendarService, Depends(CalendarService)],
            keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
            user: Annotated[UserLite, Depends(get_current_user)],
            token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
            event_create: EventCreate,
        ) -> Any:
            """
            Post event to google calendar.

            :returns EventExtra json object: the created event or exception otherwise.
            """
            logger.info(
                "User %s creating new event in calendar %s", user.id, event_create.calendar_id
            )

            user_info = await keycloak_service.get_user_info(token.credentials)

            calendar = await calendar_service.get_with_collisions(event_create.calendar_id)

            reservation_service = await calendar_service.get_reservation_service(
                calendar.id,
            )

            google_calendar_service = GoogleCalendarService()

            if not await control_collision(
                google_calendar_service,
                event_create.start_datetime,
                event_create.end_datetime,
                calendar,
            ):
                logger.warning("Collision detected for event by user %s", user.id)
                raise SoftValidationError("There's already a reservation for that time.")

            event_body = GoogleCalendarEventCreate(
                **await service.post_event(event_create, user_info.services, user, calendar)
            )
            if not event_body:
                logger.error("Failed to create event for user %s", user.id)
                raise BaseAppError(message="Could not create event.")

            return await process_event_approval(
                service,
                user,
                calendar,
                event_body,
                event_create,
                reservation_service,
            )

        @router.put(
            "/{id}/approve-time-change-request",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def approve_time_change_request(
            service: Annotated[EventService, Depends(EventService)],
            user: Annotated[UserLite, Depends(get_current_user)],
            id_: Annotated[str, Path(alias="id", description="The ID of the object.")],
            approve: bool = Query(False, description="Approve this update or not."),
            manager_notes: Annotated[str, Body()] = "-",
        ) -> Any:
            """
            Approve updating reservation time.

            Only users with special roles can approve this update.
            """
            logger.info(
                "User %s approving time change for event %s (approve=%s)", user.id, id_, approve
            )
            google_calendar_service = GoogleCalendarService()
            event: EventDetail = await service.get(id_)

            event_update: EventUpdate = EventUpdate(
                event_state=EventState.CONFIRMED,
                requested_reservation_start=None,
                requested_reservation_end=None,
            )

            if not approve:
                logger.debug("Approving requested time change for event %s", id_)
                event_to_update = await service.approve_update_reservation_time(
                    id_,
                    event_update,
                    user,
                )
                if not event_to_update:
                    raise EntityNotFoundError(Entity.EVENT, id_)

                await preparing_email(
                    service,
                    event,
                    create_email_meta(
                        "decline_update_reservation_time",
                        "Request Update Reservation Time Has Been Declined",
                        manager_notes,
                    ),
                )
            else:
                logger.debug("Declining requested time change for event %s", id_)
                event_from_google_calendar = await google_calendar_service.get_event(
                    event.calendar_id, id_
                )
                event_update.reservation_start = event.requested_reservation_start
                event_update.reservation_end = event.requested_reservation_end

                event_to_update = await service.approve_update_reservation_time(
                    id_,
                    event_update,
                    user,
                )
                if not event_to_update:
                    raise EntityNotFoundError(Entity.EVENT, id_)
                prague = timezone("Europe/Prague")
                event_from_google_calendar.start.date_time = prague.localize(
                    event.reservation_start,
                ).isoformat()
                event_from_google_calendar.end.date_time = prague.localize(
                    event.reservation_end,
                ).isoformat()
                await preparing_email(
                    service,
                    event,
                    create_email_meta(
                        "approve_update_reservation_time",
                        "Request Update Reservation Time Has Been Approved",
                        manager_notes,
                    ),
                )

                await google_calendar_service.update_event(
                    event.calendar_id, id_, event_from_google_calendar
                )

            logger.debug("Time change request processed for event %s: %s", id_, event_to_update)
            return event_to_update

        @router.put(
            "/{id}",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def update(
            service: Annotated[EventService, Depends(EventService)],
            user: Annotated[UserLite, Depends(get_current_user)],
            id_: Annotated[str, Path(alias="id", description="The ID of the object.")],
            event_update: Annotated[EventUpdate, Body()],
            reason: Annotated[str, Body()] = "",
        ) -> Any:
            """
            Update object.

            Only users with special roles can update object.
            """
            logger.info("User %s updating event %s with reason: %s", user.id, id_, reason)
            google_calendar_service = GoogleCalendarService()
            event = await service.update_with_permission_checks(id_, event_update, user)

            event_to_update = await google_calendar_service.get_event(event.calendar_id, event.id)
            event_to_update.description = service._description_of_event(user, event)
            await google_calendar_service.update_event(event.calendar_id, event.id, event_to_update)

            await preparing_email(
                service,
                event,
                create_email_meta(
                    "update_reservation",
                    "Update Reservation By Manager",
                    reason,
                ),
            )

            logger.debug("Event updated: %s", event)
            return event

        @router.put(
            "/{id}/request-time-change",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def request_time_change(
            service: Annotated[EventService, Depends(EventService)],
            user: Annotated[UserLite, Depends(get_current_user)],
            id_: Annotated[str, Path(alias="id", description="The ID of the object.")],
            event_update: Annotated[EventUpdateTime, Body()],
            reason: Annotated[str, Body()] = "",
        ) -> Any:
            """Request Update reservation time."""
            logger.info(
                "User %s requesting time change for event %s (reason=%s)", user.id, id_, reason
            )
            event: EventLite = await service.request_update_reservation_time(
                id_,
                event_update,
                user,
            )

            await preparing_email(
                service,
                event,
                create_email_meta(
                    "request_update_reservation_time",
                    "Request Update Reservation Time",
                    reason,
                ),
            )

            logger.debug("Time change request processed for event: %s", event)
            return event

        @router.put(
            "/{id}/approve",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403_404"],
            status_code=status.HTTP_200_OK,
        )
        async def approve_reservation(
            service: Annotated[EventService, Depends(EventService)],
            user: Annotated[UserLite, Depends(get_current_user)],
            id_: Annotated[str, Path(alias="id", description="The ID of the object.")],
            approve: bool = Query(False, description="Approve this reservation or not."),
            manager_notes: Annotated[str, Body()] = "-",
        ) -> Any:
            """
            Approve reservation.

            Only users with special roles can approve reservation.
            """
            logger.info(
                "User %s processing reservation approval for event %s (approve=%s)",
                user.id,
                id_,
                approve,
            )
            google_calendar_service = GoogleCalendarService()
            if approve:
                event = await service.confirm_event(id_, user)
            else:
                event = await service.cancel_event(id_, user)

            if approve:
                calendar = await service.get_calendar_of_this_event(event)
                event_to_update = await google_calendar_service.get_event(
                    event.calendar_id, event.id
                )

                event_to_update.summary = calendar.reservation_type

                await google_calendar_service.update_event(
                    event.calendar_id, event.id, event_to_update
                )

                await preparing_email(
                    service,
                    event,
                    create_email_meta(
                        "approve_reservation",
                        "Reservation Has Been Approved",
                        manager_notes,
                    ),
                )
                logger.debug("Reservation approved: %s", event)
            else:
                await google_calendar_service.delete_event(event.calendar_id, event.id)

                await preparing_email(
                    service,
                    event,
                    create_email_meta(
                        "decline_reservation",
                        "Reservation Has Been Declined",
                        manager_notes,
                    ),
                )
                logger.debug("Reservation declined: %s", event)

            return event

        @router.delete(
            "/{id}",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403_404"],
            status_code=status.HTTP_200_OK,
        )
        async def cancel(
            service: Annotated[EventService, Depends(EventService)],
            user: Annotated[UserLite, Depends(get_current_user)],
            id_: Annotated[str, Path(alias="id", description="The ID of the object.")],
            cancel_reason: Annotated[str, Body()] = "",
        ) -> Any:
            """
            Cancel event.

            Only user who make this reservation can cancel this reservation.
            """
            logger.info("User %s cancelling event %s (reason=%s)", user.id, id_, cancel_reason)
            google_calendar_service = GoogleCalendarService()
            event = await service.cancel_event(id_, user)

            await google_calendar_service.delete_event(event.calendar_id, event.id)

            if event.user_id == user.id:
                await preparing_email(
                    service,
                    event,
                    create_email_meta("cancel_reservation", "Cancel Reservation"),
                )
            else:
                await preparing_email(
                    service,
                    event,
                    create_email_meta(
                        "cancel_reservation_by_manager",
                        "Cancel Reservation by Manager",
                        cancel_reason,
                    ),
                )

            logger.debug("Event cancelled: %s", event)
            return event

        @router.delete(
            "/{id}/hard",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403_404"],
            status_code=status.HTTP_200_OK,
        )
        async def delete(
            service: Annotated[EventService, Depends(EventService)],
            user: Annotated[UserLite, Depends(get_current_user)],
            id_: Annotated[str, Path(alias="id", description="The ID of the object.")],
        ) -> Any:
            """
            Delete event.

            Only managers and if event have state canceled.
            """
            logger.info("User %s hard deleting event %s", user.id, id_)
            event = await service.delete_with_permission_checks(id_, user)
            logger.debug("Event hard deleted: %s", event)
            return event


EventRouter()
