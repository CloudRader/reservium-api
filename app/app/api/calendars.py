"""
API controllers for calendars.
"""
from typing import Any, Annotated, List
from fastapi import APIRouter, Depends, Path, status, Body
from fastapi.responses import JSONResponse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from api import EntityNotFoundException, Entity, Message, fastapi_docs, \
    auth_google, get_current_user
from schemas import CalendarCreate, Calendar, CalendarUpdate, User
from services import CalendarService

router = APIRouter(
    prefix='/calendars',
    tags=[fastapi_docs.CALENDAR_TAG["name"]]
)


# pylint: disable=no-member
@router.post("/create_calendar",
             response_model=Calendar,
             responses={
                 400: {"model": Message,
                       "description": "Couldn't create calendar."},
             },
             status_code=status.HTTP_201_CREATED)
async def create_calendar(
        service: Annotated[CalendarService, Depends(CalendarService)],
        user: Annotated[User, Depends(get_current_user)],
        calendar_create: CalendarCreate,
) -> Any:
    """
    Create calendar, only users with special roles can create calendar.

    :param service: Calendar service.
    :param user: User who make this request.
    :param calendar_create: Calendar Create schema.

    :returns CalendarModel: the created calendar.
    """
    try:
        google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
        google_calendar_service.calendars(). \
            get(calendarId=calendar_create.id).execute()
    except HttpError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "This calendar not exist in Google calendar."
            }
        )

    calendar = service.create_calendar(calendar_create, user)
    if not calendar:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Could not create calendar, because bad request or "
                           "you don't have permission for that."
            }
        )
    return calendar


@router.post("/create_calendars",
             response_model=List[Calendar],
             responses={
                 400: {"model": Message,
                       "description": "Couldn't create calendar."},
             },
             status_code=status.HTTP_201_CREATED)
async def create_calendars(
        service: Annotated[CalendarService, Depends(CalendarService)],
        user: Annotated[User, Depends(get_current_user)],
        calendars_create: List[CalendarCreate],
) -> Any:
    """
    Create calendars, only users with special roles can create calendar.

    :param service: Calendar service.
    :param user: User who make this request.
    :param calendars_create: Calendars Create schema.

    :returns CalendarModel: the created calendar.
    """
    calendars_result: List[Calendar] = []
    for calendar in calendars_create:
        calendars_result.append(
            await create_calendar(service, user, calendar)
        )

    return calendars_result


@router.get("/{calendar_id}",
            response_model=Calendar,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_calendar(
        service: Annotated[CalendarService, Depends(CalendarService)],
        calendar_id: Annotated[str, Path()]
) -> Any:
    """
    Get calendar by its uuid.

    :param service: Calendar service.
    :param calendar_id: id of the calendar.

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
async def get_all_calendars(
        service: Annotated[CalendarService, Depends(CalendarService)]
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


@router.get("/google_calendars/test/",
            status_code=status.HTTP_200_OK)
async def test(
        service: Annotated[CalendarService, Depends(CalendarService)],
) -> Any:
    """
    Test function. Don't forget delete it
    """
    calendar = service.get_by_reservation_type("Entire Space")
    test_event = service.test(calendar.id)
    if not test_event:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "You don't have permission for this operation."
            }
        )
    return test_event


@router.get("/google_calendars/",
            status_code=status.HTTP_200_OK)
async def get_all_google_calendar_to_add(
        service: Annotated[CalendarService, Depends(CalendarService)],
        user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """
    Get Calendars from Google Calendar
    that are candidates for additions

    :param service: Calendar service.
    :param user: User who make this request.

    :returns list[dict]: candidate list for additions.
    """

    calendars = service.get_all_google_calendar_to_add(user)
    if not calendars:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "You don't have permission for this operation."
            }
        )
    return calendars


@router.put("/{calendar_id}",
            response_model=Calendar,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def update_calendar(
        service: Annotated[CalendarService, Depends(CalendarService)],
        user: Annotated[User, Depends(get_current_user)],
        calendar_id: Annotated[str, Path()],
        calendar_update: Annotated[CalendarUpdate, Body()],
) -> Any:
    """
    Update calendar with id equal to calendar_id,
    only users with special roles can update calendar.

    :param service: Calendar service.
    :param user: User who make this request.
    :param calendar_id: id of the calendar.
    :param calendar_update: CalendarUpdate schema.

    :returns CalendarModel: the updated calendar.
    """
    calendar = service.update_calendar(calendar_id, calendar_update, user)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return calendar


@router.delete("/{calendar_id}",
               response_model=Calendar,
               responses={
                   **EntityNotFoundException.RESPONSE,
               },
               status_code=status.HTTP_200_OK)
async def delete_calendar(
        service: Annotated[CalendarService, Depends(CalendarService)],
        user: Annotated[User, Depends(get_current_user)],
        calendar_id: Annotated[str, Path()],
) -> Any:
    """
    Delete calendar with id equal to calendar_id,
    only users with special roles can delete calendar.

    :param service: Calendar service.
    :param user: User who make this request.
    :param calendar_id: id of the calendar.

    :returns CalendarModel: the deleted calendar.
    """
    calendar = service.delete_calendar(calendar_id, user)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return calendar


@router.get("/mini_services/{calendar_id}",
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_mini_services_by_reservation_type(
        service: Annotated[CalendarService, Depends(CalendarService)],
        calendar_id: Annotated[str, Path()]
) -> Any:
    """
    Get mini services by its reservation type.

    :param service: Calendar service.
    :param calendar_id: id of the calendar.

    :return: List mini services with type equal to service type
             or None if no such calendars exists.
    """
    mini_services = service.get_mini_services_by_reservation_type(calendar_id)
    if mini_services is None:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return mini_services
