from uuid import UUID
from googleapiclient.errors import HttpError
from typing import Any, Annotated
from fastapi import APIRouter, FastAPI, Depends, Path, status

from models import CalendarModel
from schemas import CalendarCreate
from services import CalendarService
from pydantic import BaseModel

app = FastAPI()

router = APIRouter(
    prefix='/calendars'
)


@router.post("/create_calendar")
async def create_calendar(calendar_services: Annotated[CalendarService, Depends(CalendarService)],
                          calendar_create: CalendarCreate) -> Any:
    try:
        calendar_services.create_calendar(calendar_create)
        return {"message": "Calendar is create!"}

    except HttpError as error:
        print("An error occurred:", error)


@router.delete("/{type_reservation}")
async def delete_calendar(calendar_services: Annotated[CalendarService, Depends(CalendarService)],
                          type_reservation: Annotated[str, Path()]) -> Any:
    try:
        calendar_services.delete_calendar(type_reservation)
        return {"message": "Calendar is deleted!"}

    except HttpError as error:
        print("An error occurred:", error)


@router.get("/{calendar_uuid}", response_model=CalendarModel, status_code=status.HTTP_200_OK)
async def get_calendar(calendar_services: Annotated[CalendarService, Depends(CalendarService)],
                       calendar_uuid: Annotated[UUID, Path()]) -> Any:
    # try:
    #     result = calendar_services.get(calendar_uuid)
    #     return result
    #
    # except HttpError as error:
    #     print("An error occurred:", error)
    calendar = calendar_services.get(calendar_uuid)
    if not calendar:
        raise
    return calendar
