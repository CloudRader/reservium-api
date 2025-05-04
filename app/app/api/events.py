"""
API controllers for events.
"""
from typing import Any, Annotated, List

from googleapiclient.discovery import build
from fastapi import APIRouter, Depends, status, Path
from fastapi.responses import JSONResponse
from models import ReservationServiceModel, CalendarModel, EventState
from schemas import EventCreate, Room, UserIS, InformationFromIS, \
    ServiceList, User, EmailCreate, Event
from services import EventService, CalendarService
from api import get_request, fastapi_docs, \
    get_current_user, get_current_token, auth_google, control_collision, \
    check_night_reservation, control_available_reservation_time, send_email, \
    EntityNotFoundException, Entity

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
    if not events:
        raise EntityNotFoundException(Entity.EVENT, user_id)
    return events


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
