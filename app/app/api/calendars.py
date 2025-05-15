"""
API controllers for calendars.
"""
from typing import Any, Annotated, List
from fastapi import APIRouter, Depends, Path, status, Body, Query
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from api import EntityNotFoundException, Entity, Message, fastapi_docs, \
    auth_google, get_current_user, BaseAppException, PermissionDeniedException, \
    UnauthorizedException
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
                 404: {"model": Message,
                       "description": "This calendar not exist in Google calendar."},
                 **BaseAppException.RESPONSE,
                 **PermissionDeniedException.RESPONSE,
                 **UnauthorizedException.RESPONSE,
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
    google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
    if calendar_create.id:
        try:
            google_calendar_service.calendars(). \
                get(calendarId=calendar_create.id).execute()
        except HttpError as exc:
            raise BaseAppException("This calendar not exist in Google calendar.",
                                   status_code=404) from exc
    else:
        try:
            calendar_body = {
                'summary': calendar_create.reservation_type,  # Title of the new calendar
                'timeZone': 'Europe/Prague',  # Set your desired timezone
            }
            created_calendar = (google_calendar_service.calendars().
                                insert(body=calendar_body).execute())
            calendar_create.id = created_calendar.get('id')

            rule = {
                'role': 'reader',  # Role is 'reader' for read-only public access
                'scope': {
                    'type': 'default'  # 'default' means public access
                }
            }
            (google_calendar_service.acl().
             insert(calendarId=calendar_create.id, body=rule).execute())
        except HttpError as exc:
            raise BaseAppException("Can't create calendar in Google Calendar.") from exc

    calendar = await service.create_calendar(calendar_create, user)
    if not calendar:
        raise BaseAppException()
    return calendar


@router.post("/create_calendars",
             response_model=List[Calendar],
             responses={
                 404: {"model": Message,
                       "description": "This calendar not exist in Google calendar."},
                 **BaseAppException.RESPONSE,
                 **PermissionDeniedException.RESPONSE,
                 **UnauthorizedException.RESPONSE,
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
        calendar_id: Annotated[str, Path()],
        include_removed: bool = Query(False)
) -> Any:
    """
    Get calendar by its uuid.

    :param service: Calendar service.
    :param calendar_id: id of the calendar.
    :param include_removed: include removed calendar or not.

    :return: Calendar with uuid equal to calendar_uuid
             or None if no such document exists.
    """
    calendar = await service.get(calendar_id, include_removed)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return calendar


@router.get("/",
            response_model=List[Calendar],
            responses={
                **BaseAppException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_all_calendars(
        service: Annotated[CalendarService, Depends(CalendarService)],
        include_removed: bool = Query(False)
) -> Any:
    """
    Get all calendars from database.

    :param service: Calendar service.
    :param include_removed: include removed calendars or not.

    :return: List of all calendars or None if there are no calendars in db.
    """
    calendars = await service.get_all(include_removed)
    if calendars is None:
        raise BaseAppException()
    return calendars


@router.get("/google_calendars/",
            responses={
                **BaseAppException.RESPONSE,
                **PermissionDeniedException.RESPONSE,
                **UnauthorizedException.RESPONSE,
            },
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
    google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
    google_calendars = google_calendar_service.calendarList().list().execute()

    calendars = await service.get_all_google_calendar_to_add(user, google_calendars)
    if calendars is None:
        raise BaseAppException()
    return calendars


@router.put("/{calendar_id}",
            response_model=Calendar,
            responses={
                **EntityNotFoundException.RESPONSE,
                **PermissionDeniedException.RESPONSE,
                **UnauthorizedException.RESPONSE,
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
    calendar = await service.update_calendar(calendar_id, calendar_update, user)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return calendar


@router.put("/retrieve_deleted/{calendar_id}",
            response_model=Calendar,
            responses={
                **EntityNotFoundException.RESPONSE,
                **PermissionDeniedException.RESPONSE,
                **UnauthorizedException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def retrieve_deleted_calendar(
        service: Annotated[CalendarService, Depends(CalendarService)],
        user: Annotated[User, Depends(get_current_user)],
        calendar_id: Annotated[str, Path()]
) -> Any:
    """
    Retrieve deleted calendar with uuid equal to calendar_id,
    only users with special roles can update calendar.

    :param service: Reservation Service ser.
    :param user: User who make this request.
    :param calendar_id: id of the calendar.

    :returns CalendarModel: the updated calendar.
    """
    calendar = await service.retrieve_removed_object(
        calendar_id, user
    )
    if not calendar:
        raise EntityNotFoundException(Entity.RESERVATION_SERVICE, calendar_id)
    return calendar


@router.delete("/{calendar_id}",
               response_model=Calendar,
               responses={
                   **EntityNotFoundException.RESPONSE,
                   **PermissionDeniedException.RESPONSE,
                   **UnauthorizedException.RESPONSE,
               },
               status_code=status.HTTP_200_OK)
async def delete_calendar(
        service: Annotated[CalendarService, Depends(CalendarService)],
        user: Annotated[User, Depends(get_current_user)],
        calendar_id: Annotated[str, Path()],
        hard_remove: bool = Query(False)
) -> Any:
    """
    Delete calendar with id equal to calendar_id,
    only users with special roles can delete calendar.

    :param service: Calendar service.
    :param user: User who make this request.
    :param calendar_id: id of the calendar.
    :param hard_remove: hard remove of the calendar or not.

    :returns CalendarModel: the deleted calendar.
    """
    calendar = await service.delete_calendar(calendar_id, user, hard_remove)
    if not calendar:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return calendar


@router.get("/mini_services/{calendar_id}",
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_mini_services_by_calendar(
        service: Annotated[CalendarService, Depends(CalendarService)],
        calendar_id: Annotated[str, Path()]
) -> Any:
    """
    Get mini services by its calendar.

    :param service: Calendar service.
    :param calendar_id: id of the calendar.

    :return: List mini services with type equal to service type
             or None if no such calendars exists.
    """
    mini_services = await service.get_mini_services_by_calendar(calendar_id)
    if mini_services is None:
        raise EntityNotFoundException(Entity.CALENDAR, calendar_id)
    return mini_services


@router.get("/reservation_service/{reservation_service_id}",
            response_model=List[Calendar],
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_calendars_by_reservation_service_id(
        service: Annotated[CalendarService, Depends(CalendarService)],
        reservation_service_id: Annotated[str, Path()],
        include_removed: bool = Query(False)
) -> Any:
    """
    Get calendars by its reservation service id.

    :param service: Calendar Service.
    :param reservation_service_id: reservation service id of the calendars.
    :param include_removed: include removed mini service or not.

    :return: Calendars with reservation service id equal
    to reservation service id or None if no such calendars exists.
    """
    calendars = await service.get_by_reservation_service_id(reservation_service_id,
                                                            include_removed)
    if calendars is None:
        raise BaseAppException()
    return calendars
