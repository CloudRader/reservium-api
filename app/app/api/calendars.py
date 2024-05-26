"""
API controllers for calendars.
"""
from typing import Any, Annotated, List
from fastapi import APIRouter, Depends, Path, status, Body
from fastapi.responses import JSONResponse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from api import EntityNotFoundException, Entity, Message, fastapi_docs, \
    auth_google
from schemas import CalendarCreate, Calendar, CalendarUpdate
from services import CalendarService, UserService

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
async def create_calendar(service: Annotated[CalendarService, Depends(CalendarService)],
                          user_service: Annotated[UserService, Depends(UserService)],
                          calendar_create: CalendarCreate,
                          username: str) -> Any:
    """
    Create calendar, only users with special roles can create calendar.

    :param service: Calendar service.
    :param user_service: User service.
    :param calendar_create: Calendar Create schema.
    :param username: Username of the user who will make this request.

    :returns CalendarModel: the created calendar.
    """
    try:
        google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
        google_calendar_service.calendars(). \
            get(calendarId=calendar_create.calendar_id).execute()
    except HttpError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "This calendar not exist in Google calendar."
            }
        )

    user = user_service.get_by_username(username)
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
                          user_service: Annotated[UserService, Depends(UserService)],
                          calendar_id: Annotated[str, Path()],
                          calendar_update: Annotated[CalendarUpdate, Body()],
                          username: str) -> Any:
    """
    Update calendar with id equal to calendar_id,
    only users with special roles can update calendar.

    :param service: Calendar service.
    :param user_service: User service.
    :param calendar_id: uuid of the calendar.
    :param calendar_update: CalendarUpdate schema.
    :param username: Username of the user who will make this request.

    :returns CalendarModel: the updated calendar.
    """
    user = user_service.get_by_username(username)
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
async def delete_calendar(service: Annotated[CalendarService, Depends(CalendarService)],
                          user_service: Annotated[UserService, Depends(UserService)],
                          calendar_id: Annotated[str, Path()],
                          username: str) -> Any:
    """
    Delete calendar with id equal to calendar_id,
    only users with special roles can delete calendar.

    :param service: Calendar service.
    :param user_service: User service.
    :param calendar_id: uuid of the document.
    :param username: Username of the user who will make this request.

    :returns CalendarModel: the deleted calendar.
    """
    user = user_service.get_by_username(username)
    calendar = service.delete_calendar(calendar_id, user)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return calendar


@router.get("/alias/{service_alias}",
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_reservation_types_by_alias(
        service: Annotated[CalendarService, Depends(CalendarService)],
        service_alias: Annotated[str, Path()]
) -> Any:
    """
    Get reservation types by its service alias.

    :param service: Calendar service.
    :param service_alias: service alias of the calendar.

    :return: List reservation types with alias equal to service alias
             or None if no such calendars exists.
    """
    reservation_types = service.get_reservation_type_by_service_alias(service_alias)
    if not reservation_types:
        raise EntityNotFoundException(Entity.CALENDAR, service_alias)
    return reservation_types


@router.get("/type/{reservation_type}",
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_mini_services_by_reservation_type(
        service: Annotated[CalendarService, Depends(CalendarService)],
        reservation_type: Annotated[str, Path()]
) -> Any:
    """
    Get mini services by its reservation type.

    :param service: Calendar service.
    :param reservation_type: reservation type of the calendar.

    :return: List mini services with type equal to service type
             or None if no such calendars exists.
    """
    mini_services = service.get_mini_services_by_reservation_type(reservation_type)
    if not mini_services:
        raise EntityNotFoundException(Entity.CALENDAR, reservation_type)
    return mini_services
