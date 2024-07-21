"""
API controllers for events.
"""
from typing import Any, Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from schemas import EventCreate, Room, UserIS, InformationFromIS, \
    ServiceList, User
from services import EventService
from api import get_request, fastapi_docs, \
    get_current_user, get_current_token

router = APIRouter(
    prefix='/events',
    tags=[fastapi_docs.EVENT_TAG["name"]]
)


@router.post("/post",
             status_code=status.HTTP_201_CREATED,
             )
async def post_event(
        service: Annotated[EventService, Depends(EventService)],
        user: Annotated[User, Depends(get_current_user)],
        token: Annotated[Any, Depends(get_current_token)],
        event_create: EventCreate
) -> Any:
    """
    Post event to google calendar.

    :param service: Event service.
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

    event = service.post_event(event_create, is_info, user)
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
