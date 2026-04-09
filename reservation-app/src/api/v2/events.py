"""API controllers for events."""

import logging
from typing import Annotated, Any

from api import (
    get_current_user,
)
from api.api_base import BaseCRUDRouter
from api.dependencies import http_bearer
from api.v2.emails import create_email_meta, preparing_email
from core.application.exceptions import (
    ERROR_RESPONSES,
    Entity,
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
from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from integrations.google import GoogleCalendarService
from integrations.keycloak import KeycloakAuthService
from services import EventService

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
            event_state: Annotated[
                EventState | None, Query(description="Filter events by their state.")
            ] = None,
            past: bool | None = Query(
                None,
                description="Filter events by time. `True` for past events, `False` for "
                "future events, `None` for all events.",
            ),
        ) -> Any:
            """Get events for the current user based on their roles and filters."""
            logger.info(
                "User %s fetching events by roles (state=%s, past=%s)", user.id, event_state, past
            )
            events = await service.get_events_by_user_roles(user, event_state, past)
            logger.debug("Fetched %d events for user %s", len(events), user.id)
            return events

        self.register_routes()

        @router.post(
            "/",
            responses=ERROR_RESPONSES["200_401_404"],
            status_code=status.HTTP_201_CREATED,
        )
        async def create(
            background_tasks: BackgroundTasks,
            service: Annotated[EventService, Depends(EventService)],
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

            return await service.post_event(
                background_tasks, event_create, user_info.services, user
            )

        @router.put(
            "/{id}/approve-time-change-request",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def approve_time_change_request(
            background_tasks: BackgroundTasks,
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
            return service.approve_update_reservation_time(
                id_, user, background_tasks, approve, manager_notes
            )

        @router.put(
            "/{id}",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def update(
            background_tasks: BackgroundTasks,
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
            return await service.update_with_permission_checks(
                id_, user, event_update, background_tasks, reason
            )

        @router.put(
            "/{id}/request-time-change",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def request_time_change(
            background_tasks: BackgroundTasks,
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

            return await service.request_update_reservation_time(
                id_, event_update, user, background_tasks, reason
            )

        @router.put(
            "/{id}/approve",
            response_model=EventLite,
            responses=ERROR_RESPONSES["400_401_403_404"],
            status_code=status.HTTP_200_OK,
        )
        async def approve_reservation(
            background_tasks: BackgroundTasks,
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
                    background_tasks,
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
                    background_tasks,
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
            background_tasks: BackgroundTasks,
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
                    background_tasks,
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
                    background_tasks,
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
