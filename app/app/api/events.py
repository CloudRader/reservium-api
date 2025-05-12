"""
API controllers for events.
"""
from typing import Any, Annotated, List
from dateutil.parser import isoparse
from pytz import timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import APIRouter, Depends, status, Path, Body, Query
from fastapi.responses import JSONResponse
from models import EventState
from schemas import EventCreate, ServiceList, User, Event, EventUpdate, \
    EventUpdateTime, EventWithExtraDetails
from services import EventService, CalendarService
from api import get_request, fastapi_docs, \
    get_current_user, get_current_token, auth_google, control_collision, \
    check_night_reservation, control_available_reservation_time, \
    EntityNotFoundException, Entity, PermissionDeniedException, UnauthorizedException, \
    BaseAppException, preparing_email, create_email_meta
# from api import add_or_update_access_to_reservation_areas, delete_access_to_reservation_areas

router = APIRouter(
    prefix='/events',
    tags=[fastapi_docs.EVENT_TAG["name"]]
)


# pylint: disable=no-member
# reason: The googleapiclient.discovery.build function
# dynamically creates the events attribute, which is not easily
# understood by static code analysis tools like pylint.
@router.post("/create_event",
             responses={
                 **EntityNotFoundException.RESPONSE,
             },
             status_code=status.HTTP_201_CREATED,
             )
async def create_event(
        service: Annotated[EventService, Depends(EventService)],
        calendar_service: Annotated[CalendarService, Depends(CalendarService)],
        user: Annotated[User, Depends(get_current_user)],
        token: Annotated[Any, Depends(get_current_token)],
        event_create: EventCreate
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
    services = ServiceList(services=await get_request(
        token, "/services/mine")).services

    calendar = await calendar_service.get_by_reservation_type(event_create.reservation_type)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, event_create.reservation_type)
    reservation_service = await calendar_service.get_reservation_service_of_this_calendar(
        calendar.reservation_service_id
    )
    google_calendar_service = build("calendar", "v3", credentials=auth_google(None))

    if not control_collision(google_calendar_service, event_create, calendar):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "There's already a reservation for that time."}
        )

    event_body = await service.post_event(event_create, services, user, calendar)
    if not event_body or (len(event_body) == 1 and 'message' in event_body):
        if event_body:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=event_body
            )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Could not create event."}
        )

    event_create.reservation_type = calendar.id

    if event_create.guests > calendar.max_people:
        event_body["summary"] = f"Not approved - more than {calendar.max_people} people"
        event = google_calendar_service.events().insert(calendarId=calendar.id,
                                                        body=event_body).execute()
        await service.create_event(event_create, user,
                                   EventState.NOT_APPROVED,
                                   event['id'])
        return {"message": f"more than {calendar.max_people} people"}

    if not check_night_reservation(user):
        if not control_available_reservation_time(event_create.start_datetime,
                                                  event_create.end_datetime):
            event_body["summary"] = "Not approved - night time"
            subject = event_body["summary"]
            event_google_calendar = (google_calendar_service.events().
                                     insert(calendarId=calendar.id,
                                            body=event_body).execute())
            event = await service.create_event(event_create, user,
                                               EventState.NOT_APPROVED,
                                               event_google_calendar['id'])
            await preparing_email(
                service, event,
                create_email_meta("not_approve_night_time_reservation", subject)
            )
            return {"message": "Night time"}

    event_google_calendar = google_calendar_service.events().insert(calendarId=calendar.id,
                                                                    body=event_body).execute()
    event = await service.create_event(event_create, user,
                                       EventState.CONFIRMED,
                                       event_google_calendar['id'])

    await preparing_email(
        service, event,
        create_email_meta("confirm_reservation",
                          f"{reservation_service.name} Reservation Confirmation")
    )

    # Add or update access to dormitory card system only for test
    # await add_or_update_access_to_reservation_areas(service, event)

    return event_google_calendar


@router.get("/user/{user_id}",
            response_model=List[EventWithExtraDetails],
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
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
        raise BaseAppException()
    return events


@router.get("/state/reservation_service/{reservation_service_alias}",
            response_model=List[EventWithExtraDetails],
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
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
        reservation_service_alias, event_state)
    if events is None:
        raise BaseAppException()
    return events


@router.put("/approve_update_reservation_time/{event_id}",
            response_model=Event,
            responses={
                **EntityNotFoundException.RESPONSE,
                **PermissionDeniedException.RESPONSE,
                **UnauthorizedException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def approve_update_reservation_time(
        service: Annotated[EventService, Depends(EventService)],
        user: Annotated[User, Depends(get_current_user)],
        event_id: Annotated[str, Path()],
        approve: bool = Query(False),
        manager_notes: Annotated[str, Body()] = "-",
) -> Any:
    """
    Approve updating reservation time,
    only users with special roles can approve this update.

    :param service: Event service.
    :param user: User who make this request.
    :param event_id: uuid of the event.
    :param approve: Approve this update or not.
    :param manager_notes: Note for update or decline update reservation time.

    :returns EventModel: the updated event.
    """
    google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
    event: Event = await service.get(event_id)
    if not event:
        raise EntityNotFoundException(Entity.EVENT, event_id)
    try:
        event_update: EventUpdate = EventUpdate(event_state=EventState.CONFIRMED)
        event_from_google_calendar = google_calendar_service.events().get(
            calendarId=event.calendar_id,
            eventId=event.id
        ).execute()
        if not approve:
            event_update.start_datetime = (isoparse(event_from_google_calendar["start"]["dateTime"])
                                           .replace(tzinfo=None))
            event_update.end_datetime = (isoparse(event_from_google_calendar["end"]["dateTime"])
                                         .replace(tzinfo=None))
            event_to_update = await service.approve_update_reservation_time(
                event_id, event_update, user
            )
            if not event_to_update:
                raise EntityNotFoundException(Entity.EVENT, event_id)

            await preparing_email(
                service, event,
                create_email_meta("decline_update_reservation_time",
                                  "Request Update Reservation Time Has Been Declined",
                                  manager_notes)
            )
        else:
            event_to_update = await service.approve_update_reservation_time(
                event_id, event_update, user
            )
            if not event_to_update:
                raise EntityNotFoundException(Entity.EVENT, event_id)
            prague = timezone("Europe/Prague")
            event_from_google_calendar["start"]["dateTime"] = prague.localize(
                event.start_datetime).isoformat()
            event_from_google_calendar["end"]["dateTime"] = prague.localize(
                event.end_datetime).isoformat()
            await preparing_email(
                service, event,
                create_email_meta("approve_update_reservation_time",
                                  "Request Update Reservation Time Has Been Approved",
                                  manager_notes)
            )

            google_calendar_service.events().update(
                calendarId=event.calendar_id,
                eventId=event.id,
                body=event_from_google_calendar
            ).execute()

            # Add or update access to dormitory card system only for test
            # await add_or_update_access_to_reservation_areas(service, event)

        return event_to_update

    except HttpError as exc:
        raise BaseAppException("Something went wrong, control updating data.",
                               ) from exc


@router.put("/request_update_reservation_time/{event_id}",
            response_model=Event,
            responses={
                **EntityNotFoundException.RESPONSE,
                **PermissionDeniedException.RESPONSE,
                **UnauthorizedException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def request_update_reservation_time(
        service: Annotated[EventService, Depends(EventService)],
        user: Annotated[User, Depends(get_current_user)],
        event_id: Annotated[str, Path()],
        event_update: Annotated[EventUpdateTime, Body()],
        reason: Annotated[str, Body()] = "",
) -> Any:
    """
    Request Update reservation time with uuid equal to event_id,
    only user that create this reservation can request it.

    :param service: Event service.
    :param user: User who make this request.
    :param event_id: uuid of the event.
    :param event_update: EventUpdate schema.
    :param reason: Reason to change reservation time.

    :returns EventModel: the updated event.
    """
    event: Event = await service.request_update_reservation_time(
        event_id, event_update, user
    )
    if not event:
        raise EntityNotFoundException(Entity.EVENT, event_id)
    await preparing_email(
        service, event,
        create_email_meta("request_update_reservation_time",
                          "Request Update Reservation Time", reason)
    )
    return event


@router.delete("/{event_id}",
               response_model=Event,
               responses={
                   **EntityNotFoundException.RESPONSE,
                   **PermissionDeniedException.RESPONSE,
                   **UnauthorizedException.RESPONSE,
               },
               status_code=status.HTTP_200_OK)
async def cancel_reservation(
        service: Annotated[EventService, Depends(EventService)],
        user: Annotated[User, Depends(get_current_user)],
        event_id: Annotated[str, Path()],
        cancel_reason: Annotated[str, Body()] = "",
) -> Any:
    """
    Delete event with id equal to event_id, only user who make
    this reservation can cancel this reservation.

    :param service: Event service.
    :param user: User who make this reservation.
    :param event_id: id of the event.
    :param cancel_reason: reason cancellation this reservation.

    :returns EventModel: the canceled reservation.
    """
    google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
    event = await service.cancel_event(event_id, user)
    if not event:
        raise EntityNotFoundException(Entity.EVENT, event_id)
    try:
        google_calendar_service.events().delete(
            calendarId=event.calendar_id,
            eventId=event.id
        ).execute()

        if event.user_id == user.id:
            await preparing_email(
                service, event,
                create_email_meta("cancel_reservation",
                                  "Cancel Reservation")
            )
        else:
            await preparing_email(
                service, event,
                create_email_meta("cancel_reservation_by_manager",
                                  "Cancel Reservation by Manager", cancel_reason)
            )

        # Delete access to dormitory card system only for test
        # await delete_access_to_reservation_areas(service, event)

        return event

    except HttpError as exc:
        raise BaseAppException("This event does not exist in Google Calendar.",
                               status_code=404) from exc


@router.put("/approve_event/{event_id}",
            response_model=Event,
            responses={
                **EntityNotFoundException.RESPONSE,
                **PermissionDeniedException.RESPONSE,
                **UnauthorizedException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def approve_reservation(
        service: Annotated[EventService, Depends(EventService)],
        user: Annotated[User, Depends(get_current_user)],
        event_id: Annotated[str, Path()],
        approve: bool = Query(False),
        manager_notes: Annotated[str, Body()] = "-",
) -> Any:
    """
    Approve reservation with uuid equal to event_id,
    only users with special roles can approve reservation.

    :param service: Event service.
    :param user: User who make this approve.
    :param event_id: uuid of the event.
    :param approve: Approve this reservation or not.
    :param manager_notes: Note for approve or decline reservation.

    :returns EventModel: the updated reservation.
    """
    google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
    if approve:
        event = await service.confirm_event(event_id, user)
        if not event:
            raise EntityNotFoundException(Entity.EVENT, event_id)
    else:
        event = await service.cancel_event(event_id, user)
        if not event:
            raise EntityNotFoundException(Entity.EVENT, event_id)
    try:
        if approve:
            calendar = await service.get_calendar_of_this_event(event)
            event_to_update = google_calendar_service.events().get(
                calendarId=event.calendar_id,
                eventId=event.id
            ).execute()

            event_to_update['summary'] = calendar.reservation_type

            google_calendar_service.events().update(
                calendarId=event.calendar_id,
                eventId=event.id,
                body=event_to_update
            ).execute()

            await preparing_email(
                service, event,
                create_email_meta("approve_reservation",
                                  "Reservation Has Been Approved", manager_notes)
            )

            # Add or update access to dormitory card system only for test
            # await add_or_update_access_to_reservation_areas(service, event)

        else:
            google_calendar_service.events().delete(
                calendarId=event.calendar_id,
                eventId=event.id
            ).execute()

            await preparing_email(
                service, event,
                create_email_meta("decline_reservation",
                                  "Reservation Has Been Declined", manager_notes)
            )

        return event

    except HttpError as exc:
        raise BaseAppException("This event does not exist in Google Calendar.",
                               status_code=404) from exc
