"""
API controllers for events.
"""
from googleapiclient.errors import HttpError
from typing import Any

from fastapi import APIRouter
from fastapi import FastAPI
from schemas import EventInput, User, Room, UserIS
from services import EventService
from api.google_auth import auth_google
import httpx

app = FastAPI()

router = APIRouter(
    prefix='/events'
)


def read_token_from_file(file_path="token.txt"):
    try:
        with open(file_path, "r") as token_file:
            token = token_file.read().strip()
            return token
    except FileNotFoundError:
        print(f"Token file '{file_path}' not found.")
        return None


async def get_request(token: str, request: str):
    info_endpoint = "https://api.is.buk.cvut.cz/v1" + request

    async with httpx.AsyncClient() as client:
        response = await client.get(info_endpoint, headers={"Authorization": f"Bearer {token}"})
        response_data = response.json()

    return response_data


@router.post("/create_event")
async def create_event(event_input: EventInput) -> Any:
    creds = auth_google(None)
    token = read_token_from_file()

    user = UserIS.model_validate(await get_request(token, "/users/me"))
    services = await get_request(token, "/services/mine")
    room = Room.model_validate(await get_request(token, "/rooms/mine"))

    try:

        service_event = EventService()
        return service_event.post_event(event_input, user, room, creds, services)

    except HttpError as error:
        print("An error occurred:", error)