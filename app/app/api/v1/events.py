"""API controllers for events."""

from typing import Annotated, Any

from api import (
    ERROR_RESPONSES,
    BaseAppError,
    Entity,
    EntityNotFoundError,
    SoftValidationError,
    fastapi_docs,
    get_current_token,
    get_current_user,
    get_request,
)
from api.external_api.google.google_calendar_services import GoogleCalendarService
from api.utils import control_collision, process_event_approval
from api.v1.emails import create_email_meta, preparing_email
from core.models import EventState
from core.schemas import (
    Event,
    EventCreate,
    EventUpdate,
    EventUpdateTime,
    EventWithExtraDetails,
    ServiceList,
    User,
)
from core.schemas.google_calendar import GoogleCalendarEventCreate
from dateutil.parser import isoparse
from fastapi import APIRouter, Body, Depends, Path, Query, status
from pytz import timezone
from services import CalendarService, EventService

router = APIRouter(tags=[fastapi_docs.EVENT_TAG["name"]])


@router.post(
    "/create_event",
    responses=ERROR_RESPONSES["404"],
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    service: Annotated[EventService, Depends(EventService)],
    calendar_service: Annotated[CalendarService, Depends(CalendarService)],
    user: Annotated[User, Depends(get_current_user)],
    token: Annotated[Any, Depends(get_current_token)],
    event_create: EventCreate,
) -> Any:
    """
    Post event to google calendar.

    :param service: Event service.
    :param calendar_service: Calendar service.
    :param user: User who make this request.
    :param token: Token for user identification.
    :param event_create: EventCreate schema.

    :returns Event json object: the created event or exception otherwise.
    """
    services = ServiceList(services=await get_request(token, "/services/mine")).services

    calendar = await calendar_service.get(event_create.calendar_id)
    if not calendar:
        raise EntityNotFoundError(Entity.CALENDAR, event_create.calendar_id)
    reservation_service = await calendar_service.get_reservation_service_of_this_calendar(
        calendar.reservation_service_id,
    )

    google_calendar_service = GoogleCalendarService()

    if not await control_collision(google_calendar_service, event_create, calendar):
        raise SoftValidationError("There's already a reservation for that time.")

    event_body = GoogleCalendarEventCreate(
        **await service.post_event(event_create, services, user, calendar)
    )
    if not event_body:
        raise BaseAppError(message="Could not create event.")

    return await process_event_approval(
        service,
        user,
        calendar,
        event_body,
        event_create,
        reservation_service,
    )


@router.get(
    "/user/{user_id}",
    response_model=list[EventWithExtraDetails],
    responses=ERROR_RESPONSES["400"],
    status_code=status.HTTP_200_OK,
)
async def get_events_by_user_id(
    service: Annotated[EventService, Depends(EventService)],
    user_id: Annotated[int, Path()],
) -> Any:
    """
    Get events by its user id.

    :param service: Event service.
    :param user_id: user id of the events.

    :return: Events with user id equal
    to user id or None if no such events exists.
    """
    events = await service.get_by_user_id(user_id)
    if events is None:
        raise BaseAppError()
    return events


@router.get(
    "/state/reservation_service/{reservation_service_alias}",
    response_model=list[EventWithExtraDetails],
    responses=ERROR_RESPONSES["400"],
    status_code=status.HTTP_200_OK,
)
async def get_by_event_state_by_reservation_service_alias(
    service: Annotated[EventService, Depends(EventService)],
    reservation_service_alias: Annotated[str, Path()],
    event_state: EventState,
) -> Any:
    """
    Get events by its reservation service alias.

    :param service: Event service.
    :param reservation_service_alias: reservation service id of the events.
    :param event_state: event state of the event.

    :return: Events with reservation service alias equal
    to reservation service alias or None if no such events exists.
    """
    events = await service.get_by_event_state_by_reservation_service_alias(
        reservation_service_alias,
        event_state,
    )
    if events is None:
        raise BaseAppError()
    return events


@router.put(
    "/approve_update_reservation_time/{event_id}",
    response_model=Event,
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def approve_update_reservation_time(
    service: Annotated[EventService, Depends(EventService)],
    user: Annotated[User, Depends(get_current_user)],
    event_id: Annotated[str, Path()],
    approve: bool = Query(False),
    manager_notes: Annotated[str, Body()] = "-",
) -> Any:
    """
    Approve updating reservation time.

    Only users with special roles can approve this update.

    :param service: Event service.
    :param user: User who make this request.
    :param event_id: uuid of the event.
    :param approve: Approve this update or not.
    :param manager_notes: Note for update or decline update reservation time.

    :returns EventModel: the updated event.
    """
    google_calendar_service = GoogleCalendarService()
    event: Event = await service.get(event_id)
    if not event:
        raise EntityNotFoundError(Entity.EVENT, event_id)

    event_update: EventUpdate = EventUpdate(event_state=EventState.CONFIRMED)
    event_from_google_calendar = await google_calendar_service.get_event(
        event.calendar_id, event_id
    )

    if not approve:
        event_update.start_datetime = isoparse(
            event_from_google_calendar.start.date_time,
        ).replace(tzinfo=None)
        event_update.end_datetime = isoparse(
            event_from_google_calendar.end.date_time,
        ).replace(tzinfo=None)
        event_to_update = await service.approve_update_reservation_time(
            event_id,
            event_update,
            user,
        )
        if not event_to_update:
            raise EntityNotFoundError(Entity.EVENT, event_id)

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
        event_to_update = await service.approve_update_reservation_time(
            event_id,
            event_update,
            user,
        )
        if not event_to_update:
            raise EntityNotFoundError(Entity.EVENT, event_id)
        prague = timezone("Europe/Prague")
        event_from_google_calendar.start.date_time = prague.localize(
            event.start_datetime,
        ).isoformat()
        event_from_google_calendar.end.date_time = prague.localize(
            event.end_datetime,
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
            event.calendar_id, event_id, event_from_google_calendar
        )

    return event_to_update


@router.put(
    "/request_update_reservation_time/{event_id}",
    response_model=Event,
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def request_update_reservation_time(
    service: Annotated[EventService, Depends(EventService)],
    user: Annotated[User, Depends(get_current_user)],
    event_id: Annotated[str, Path()],
    event_update: Annotated[EventUpdateTime, Body()],
    reason: Annotated[str, Body()] = "",
) -> Any:
    """
    Request Update reservation time with uuid equal to 'event_id'.

    Only user that create this reservation can request it.

    :param service: Event service.
    :param user: User who make this request.
    :param event_id: uuid of the event.
    :param event_update: EventUpdate schema.
    :param reason: Reason to change reservation time.

    :returns EventModel: the updated event.
    """
    event: Event = await service.request_update_reservation_time(
        event_id,
        event_update,
        user,
    )
    if not event:
        raise EntityNotFoundError(Entity.EVENT, event_id)
    await preparing_email(
        service,
        event,
        create_email_meta(
            "request_update_reservation_time",
            "Request Update Reservation Time",
            reason,
        ),
    )
    return event


@router.delete(
    "/{event_id}",
    response_model=Event,
    responses=ERROR_RESPONSES["400_401_403_404"],
    status_code=status.HTTP_200_OK,
)
async def cancel_reservation(
    service: Annotated[EventService, Depends(EventService)],
    user: Annotated[User, Depends(get_current_user)],
    event_id: Annotated[str, Path()],
    cancel_reason: Annotated[str, Body()] = "",
) -> Any:
    """
    Delete event with id equal to 'event_id'.

    Only user who make this reservation can cancel this reservation.

    :param service: Event service.
    :param user: User who make this reservation.
    :param event_id: id of the event.
    :param cancel_reason: reason cancellation this reservation.

    :returns EventModel: the canceled reservation.
    """
    # TODO: can't delete after it ended, but can delete after it started or think about it
    google_calendar_service = GoogleCalendarService()
    event = await service.cancel_event(event_id, user)
    if not event:
        raise EntityNotFoundError(Entity.EVENT, event_id)

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

    return event


@router.put(
    "/approve_event/{event_id}",
    response_model=Event,
    responses=ERROR_RESPONSES["400_401_403_404"],
    status_code=status.HTTP_200_OK,
)
async def approve_reservation(
    service: Annotated[EventService, Depends(EventService)],
    user: Annotated[User, Depends(get_current_user)],
    event_id: Annotated[str, Path()],
    approve: bool = Query(False),
    manager_notes: Annotated[str, Body()] = "-",
) -> Any:
    """
    Approve reservation with uuid equal to 'event_id'.

    Only users with special roles can approve reservation.

    :param service: Event service.
    :param user: User who make this approve.
    :param event_id: uuid of the event.
    :param approve: Approve this reservation or not.
    :param manager_notes: Note for approve or decline reservation.

    :returns EventModel: the updated reservation.
    """
    google_calendar_service = GoogleCalendarService()
    if approve:
        event = await service.confirm_event(event_id, user)
        if not event:
            raise EntityNotFoundError(Entity.EVENT, event_id)
    else:
        event = await service.cancel_event(event_id, user)
        if not event:
            raise EntityNotFoundError(Entity.EVENT, event_id)

    if approve:
        calendar = await service.get_calendar_of_this_event(event)
        event_to_update = await google_calendar_service.get_event(event.calendar_id, event.id)

        event_to_update.summary = calendar.reservation_type

        await google_calendar_service.update_event(event.calendar_id, event.id, event_to_update)

        await preparing_email(
            service,
            event,
            create_email_meta(
                "approve_reservation",
                "Reservation Has Been Approved",
                manager_notes,
            ),
        )

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

    return event
