"""
API controllers for calendars.
"""
from typing import Any, Annotated, List
from fastapi import APIRouter, FastAPI, Depends, Path, status, Body
from fastapi.responses import JSONResponse

from api import EntityNotFoundException, Entity, Message
from schemas import CalendarCreate, Calendar, CalendarUpdate
from services import CalendarService

app = FastAPI()

router = APIRouter(
    prefix='/calendars'
)


@router.post("/create_calendar",
             response_model=Calendar,
             responses={
                 400: {"model": Message,
                       "description": "Couldn't create calendar."},
             },
             status_code=status.HTTP_201_CREATED)
async def create_calendar(service: Annotated[CalendarService, Depends(CalendarService)],
                          calendar_create: CalendarCreate) -> Any:
    """
    Create calendar.

    :param service: Document service.
    :param calendar_create: Calendar Create schema.
    """
    calendar = service.create_calendar(calendar_create)
    if not calendar:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Could not create calendar."
            }
        )
    return calendar


@router.get("/{calendar_id}",
            response_model=Calendar,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_calendar(service: Annotated[CalendarService, Depends(CalendarService)],
                       calendar_id: Annotated[str, Path()]) -> Any:
    """
    Get calendar by its uuid.

    :param service: Calendar service.
    :param calendar_id: uuid of the calendar.

    :return: Calendar with uuid equal to calendar_uuid
             or None if no such document exists.
    """
    calendar = service.get(calendar_id)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return calendar


@router.get("/",
            response_model=List[Calendar],
            status_code=status.HTTP_200_OK)
async def get_all_calendars(service: Annotated[CalendarService, Depends(CalendarService)]
                            ) -> Any:
    """
    Get all calendars from database.

    :param service: Calendar service.

    :return: List of all calendars or None if there are no calendars in db.
    """
    calendars = service.get_all()
    if not calendars:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "No calendars in db."
            }
        )
    return calendars


@router.put("/{calendar_id}",
            response_model=Calendar,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def update_calendar(service: Annotated[CalendarService, Depends(CalendarService)],
                          calendar_id: Annotated[str, Path()],
                          calendar_update: Annotated[CalendarUpdate, Body()]) -> Any:
    """
    Update calendar with id equal to calendar_id.

    :param service: Calendar service.
    :param calendar_id: uuid of the calendar.
    :param calendar_update: CalendarUpdate schema.
    """
    calendar = service.update(calendar_id, calendar_update)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return calendar


@router.delete("/{calendar_id}",
               response_model=Calendar,
               responses={
                   **EntityNotFoundException.RESPONSE,
               },
               status_code=status.HTTP_200_OK)
async def delete_calendar(service: Annotated[CalendarService, Depends(CalendarService)],
                          calendar_id: Annotated[str, Path()]) -> Any:
    """Delete calendar with id equal to calendar_id.

    :param service: Document service.
    :param calendar_id: uuid of the document.
    """
    calendar = service.delete_calendar(calendar_id)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return calendar
