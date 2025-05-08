"""
API controllers for events.
"""
from typing import Any, Annotated, List
from uuid import UUID
from datetime import timezone
from dateutil.parser import isoparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import APIRouter, Depends, status, Path, Body, Query
from fastapi.responses import JSONResponse
from models import ReservationServiceModel, CalendarModel, EventState
from schemas import EventCreate, Room, UserIS, InformationFromIS, \
    ServiceList, User, EmailCreate, Event, EventUpdate, EventUpdateTime
from services import EventService, CalendarService
from api import get_request, fastapi_docs, \
    get_current_user, get_current_token, auth_google, control_collision, \
    check_night_reservation, control_available_reservation_time, send_email, \
    EntityNotFoundException, Entity, PermissionDeniedException, UnauthorizedException, \
    BaseAppException

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
    user_is = UserIS.model_validate(await get_request(token, "/users/me"))
    services = ServiceList(services=await get_request(token,
                                                      "/services/mine")).services
    room = Room.model_validate(await get_request(token, "/rooms/mine"))
    is_info = InformationFromIS(user=user_is, room=room, services=services)

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

    event_body = await service.post_event(event_create, is_info, user, calendar)
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

    email_create = preparing_email(
        event_create, event_body, reservation_service, calendar
    )
    event_create.reservation_type = calendar.id

    if event_create.guests > calendar.max_people:
        event_body["summary"] = f"Not approved - more than {calendar.max_people} people"
        email_create.subject = event_body["summary"]
        await send_email(email_create)
        event = google_calendar_service.events().insert(calendarId=calendar.id,
                                                        body=event_body).execute()
        await service.create_event(event_create, user,
                                   EventState.NOT_APPROVED,
                                   event['id'])
        return {"message": f"more than {calendar.max_people} people"}

    # Check night reservation
    if not check_night_reservation(user):
        if not control_available_reservation_time(event_create.start_datetime,
                                                  event_create.end_datetime):
            event_body["summary"] = "Not approved - night time"
            email_create.subject = event_body["summary"]
            await send_email(email_create)
            event = google_calendar_service.events().insert(calendarId=calendar.id,
                                                            body=event_body).execute()
            await service.create_event(event_create, user,
                                       EventState.NOT_APPROVED,
                                       event['id'])
            return {"message": "Night time"}

    await send_email(email_create)
    event = google_calendar_service.events().insert(calendarId=calendar.id,
                                                    body=event_body).execute()
    await service.create_event(event_create, user,
                               EventState.CONFIRMED,
                               event['id'])
    return event


@router.get("/user/{user_id}",
            response_model=List[Event],
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


@router.get("/state/reservation_service/{reservation_service_id}",
            response_model=List[Event],
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_by_event_state_by_reservation_service_id(
        service: Annotated[EventService, Depends(EventService)],
        reservation_service_id: Annotated[UUID, Path()],
        event_state: EventState,
) -> Any:
    """
    Get events by its reservation service id.

    :param service: Event service.
    :param reservation_service_id: reservation service id of the events.
    :param event_state: event state of the event.

    :return: Events with reservation service id equal
    to reservation service id or None if no such events exists.
    """
    events = await service.get_by_event_state_by_reservation_service_id(
        reservation_service_id, event_state)
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
) -> Any:
    """
    Approve updating reservation time,
    only users with special roles can approve this update.

    :param service: Event service.
    :param user: User who make this request.
    :param event_id: uuid of the event.
    :param approve: Approve this update or not.

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
        else:
            event_to_update = await service.approve_update_reservation_time(
                event_id, event_update, user
            )
            if not event_to_update:
                raise EntityNotFoundException(Entity.EVENT, event_id)
            event_from_google_calendar["start"]["dateTime"] = (
                event_to_update.start_datetime.astimezone(timezone.utc).isoformat())
            event_from_google_calendar["end"]["dateTime"] = (
                event_to_update.end_datetime.astimezone(timezone.utc).isoformat())

            google_calendar_service.events().update(
                calendarId=event.calendar_id,
                eventId=event.id,
                body=event_from_google_calendar
            ).execute()


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
) -> Any:
    """
    Request Update reservation time with uuid equal to event_id,
    only user that create this reservation can request it.

    :param service: Event service.
    :param user: User who make this request.
    :param event_id: uuid of the event.
    :param event_update: EventUpdate schema.

    :returns EventModel: the updated event.
    """
    event: Event = await service.request_update_reservation_time(
        event_id, event_update, user
    )
    if not event:
        raise EntityNotFoundException(Entity.EVENT, event_id)
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
        event_id: Annotated[str, Path()]
) -> Any:
    """
    Delete event with id equal to event_id, only user who make
    this reservation can cancel this reservation.

    :param service: Event service.
    :param user: User who make this reservation.
    :param event_id: id of the event.

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
        calendar_service: Annotated[CalendarService, Depends(CalendarService)],
        user: Annotated[User, Depends(get_current_user)],
        event_id: Annotated[str, Path()]
) -> Any:
    """
    Approve reservation with uuid equal to event_id,
    only users with special roles can approve reservation.

    :param service: Event service.
    :param calendar_service: Calendar service.
    :param user: User who make this approve.
    :param event_id: uuid of the event.

    :returns EventModel: the updated reservation.
    """
    google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
    event = await service.confirm_event(event_id, user)
    if not event:
        raise EntityNotFoundException(Entity.EVENT, event_id)
    try:
        calendar = await calendar_service.get(event.calendar_id)
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

        return event

    except HttpError as exc:
        raise BaseAppException("This event does not exist in Google Calendar.",
                               status_code=404) from exc


def preparing_email(
        event_create: EventCreate,
        event_body: dict,
        reservation_service: ReservationServiceModel,
        calendar: CalendarModel,
) -> EmailCreate:
    """
    Constructing the body of the email .

    :param event_create: EventCreate schema.
    :param event_body: Dict body of the event.
    :param reservation_service: Reservation Service object in db.
    :param reservation_service: Calendar object in db.
    :param calendar: Calendar object in db.

    :return: Constructed EmailCreate schema.
    """
    formatted_start_date = event_create.start_datetime.strftime("%d/%m/%Y, %H:%M:%S")
    formatted_end_date = event_create.end_datetime.strftime("%d/%m/%Y, %H:%M:%S")

    return EmailCreate(
        email=[reservation_service.contact_mail],
        subject=f"{reservation_service.name} Reservation",
        body=(
            f"{calendar.reservation_type}\n\n"
            f"{formatted_start_date} - {formatted_end_date}\n\n"
            f"{event_body['description']}\n"
        ),
    )
