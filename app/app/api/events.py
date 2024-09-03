"""
API controllers for events.
"""
from typing import Any, Annotated

from googleapiclient.discovery import build
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from schemas import EventCreate, Room, UserIS, InformationFromIS, \
    ServiceList, User
from services import EventService, CalendarService
from api import get_request, fastapi_docs, \
    get_current_user, get_current_token, auth_google, control_collision, \
    check_night_reservation, control_available_reservation_time

router = APIRouter(
    prefix='/events',
    tags=[fastapi_docs.EVENT_TAG["name"]]
)


# pylint: disable=no-member
# reason: The googleapiclient.discovery.build function
# dynamically creates the events attribute, which is not easily
# understood by static code analysis tools like pylint.
@router.post("/create_event",
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

    calendar = calendar_service.get_by_reservation_type(event_create.reservation_type)
    google_calendar_service = build("calendar", "v3", credentials=auth_google(None))

    if not control_collision(google_calendar_service, event_create, calendar):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "There's already a reservation for that time."}
        )

    event_body = service.post_event(event_create, is_info, user, calendar)
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

    if event_create.guests > calendar.max_people:
        event_body["summary"] = f"Not approved - more than {calendar.max_people} people"
        google_calendar_service.events().insert(calendarId=calendar.id,
                                                body=event_body).execute()
        return {"message": "Too many people!"
                           "You need get permission from the dormitory head, "
                           "after you will be automatically created a reservation or "
                           "will be canceled with explanation of the reason from the manager."}

    # Check night reservation
    if not check_night_reservation(user):
        event_body["summary"] = "Not approved - night time"
        if not control_available_reservation_time(event_create.start_datetime,
                                                  event_create.end_datetime):
            google_calendar_service.events().insert(calendarId=calendar.id,
                                                    body=event_body).execute()
            return {"message": "Request for a night reservation has been sent to the manager, "
                               "awaiting a response. Please note that the manager "
                               "may reject a night reservation without giving a reason."}

    return google_calendar_service.events().insert(calendarId=calendar.id,
                                                   body=event_body).execute()
