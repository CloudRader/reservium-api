"""
API controllers for events.
"""
from typing import Any, Annotated

from googleapiclient.discovery import build
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from schemas import EventCreate, Room, UserIS, InformationFromIS, ServiceList
from services import EventService, UserService
from api import get_request, auth_google, fastapi_docs

router = APIRouter(
    prefix='/events',
    tags=[fastapi_docs.EVENT_TAG["name"]]
)


@router.post("/post",
             status_code=status.HTTP_201_CREATED,
             )
async def post_event(service: Annotated[EventService, Depends(EventService)],
                     user_service: Annotated[UserService, Depends(UserService)],
                     event_create: EventCreate) -> Any:
    """
    Post event to google calendar.

    :param service: Event service.
    :param user_service: User service.
    :param event_create: EventCreate schema.

    :returns Event json object: the created event or exception otherwise.
    """
    google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
    user = user_service.get_by_username(event_create.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not exist."
        )

    user_is = UserIS.model_validate(await get_request(user.user_token, "/users/me"))
    services = ServiceList(services=await get_request(user.user_token,
                                                      "/services/mine")).services
    room = Room.model_validate(await get_request(user.user_token, "/rooms/mine"))
    is_buk = InformationFromIS(user=user_is, room=room, services=services)

    event = service.post_event(event_create, is_buk, user,
                               google_calendar_service)
    if not event or (len(event) == 1 and 'message' in event):
        if event:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=event
            )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Could not create event."}
        )
    return event
