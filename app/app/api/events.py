"""
API controllers for events.
"""
from googleapiclient.errors import HttpError
from typing import Any, Annotated

from fastapi import APIRouter, FastAPI, Depends
from schemas import EventInput, Room, UserIS
from services import EventService, UserService
from api import get_request, auth_google
from schemas.user_is import RoleList, Role

app = FastAPI()

router = APIRouter(
    prefix='/events'
)


@router.post("/create_event")
async def create_event(event_service: Annotated[EventService, Depends(EventService)],
                       user_service: Annotated[UserService, Depends(UserService)],
                       event_input: EventInput) -> Any:
    creds = auth_google(None)
    user = user_service.get_by_username(event_input.username)

    user_is = UserIS.model_validate(await get_request(user.user_token, "/users/me", user_service))
    services = await get_request(user.user_token, "/services/mine", user_service)
    room = Room.model_validate(await get_request(user.user_token, "/rooms/mine", user_service))

    try:
        return event_service.post_event(event_input, user_is, user, room, creds, services)

    except HttpError as error:
        print("An error occurred:", error)
