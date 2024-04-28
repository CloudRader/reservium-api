"""
API controllers for events.
"""
from googleapiclient.errors import HttpError
from typing import Any, Annotated

from fastapi import APIRouter, FastAPI, Depends
from schemas import EventInput, Room, UserIS
from services import StudyRoomService, UserService
from api.google_auth import auth_google
from api.utils import get_request

app = FastAPI()

router = APIRouter(
    prefix='/study_rooms'
)


@router.post("/create_study_rooms_reservation")
async def create_study_room_event(study_room_service: Annotated[StudyRoomService, Depends(StudyRoomService)],
                                  user_service: Annotated[UserService, Depends(UserService)],
                                  event_input: EventInput) -> Any:
    creds = auth_google(None)
    token = user_service.get_by_username(event_input.username).user_token

    user = UserIS.model_validate(await get_request(token, "/users/me"))
    services = await get_request(token, "/services/mine")
    room = Room.model_validate(await get_request(token, "/rooms/mine"))

    try:
        return study_room_service.post_event(event_input, user, room, creds, services)

    except HttpError as error:
        print("An error occurred:", error)
