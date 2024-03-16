"""
API controllers for events.
"""
from googleapiclient.errors import HttpError
from typing import Any

from fastapi import APIRouter
from fastapi import FastAPI
from schemas import EventInput, Room, UserIS
from services import StudyRoomService
from api.google_auth import auth_google
from api.utils import get_request, read_token_from_file

app = FastAPI()

router = APIRouter(
    prefix='/study_rooms'
)


@router.post("/create_study_rooms_reservation")
async def create_study_room_event(event_input: EventInput) -> Any:
    creds = auth_google(None)
    token = read_token_from_file()

    user = UserIS.model_validate(await get_request(token, "/users/me"))
    services = await get_request(token, "/services/mine")
    room = Room.model_validate(await get_request(token, "/rooms/mine"))

    try:

        service_grill = StudyRoomService()
        return service_grill.post_event(event_input, user, room, creds, services)

    except HttpError as error:
        print("An error occurred:", error)
