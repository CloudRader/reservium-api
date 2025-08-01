"""API controllers for calendars."""

from typing import Annotated, Any

from api import (
    ERROR_RESPONSES,
    BaseAppError,
    Entity,
    EntityNotFoundError,
    fastapi_docs,
    get_current_user,
)
from api.external_api.google.google_calendar_services import GoogleCalendarService
from core.schemas import Calendar, CalendarCreate, CalendarUpdate, User
from fastapi import APIRouter, Body, Depends, Path, Query, status
from services import CalendarService

router = APIRouter(tags=[fastapi_docs.CALENDAR_TAG["name"]])


@router.get(
    "/",
    response_model=list[Calendar],
    responses=ERROR_RESPONSES["400"],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    service: Annotated[CalendarService, Depends(CalendarService)],
    include_removed: bool = Query(False),
) -> Any:
    """
    Get all calendars from database.

    :param service: Calendar service.
    :param include_removed: include removed calendars or not.

    :return: List of all calendars or None if there are no calendars in db.
    """
    calendars = await service.get_all(include_removed)
    if calendars is None:
        raise BaseAppError()
    return calendars


@router.get(
    "/{calendar_id}/mini_services",
    responses=ERROR_RESPONSES["404"],
    status_code=status.HTTP_200_OK,
    deprecated=True,
)
async def get_mini_services_by_calendar(
    service: Annotated[CalendarService, Depends(CalendarService)],
    calendar_id: Annotated[str, Path()],
) -> Any:
    """
    Get mini services by its calendar (DEPRECATED!!!).

    :param service: Calendar service.
    :param calendar_id: id of the calendar.

    :return: List mini services with type equal to service type
             or None if no such calendars exists.
    """
    mini_services = await service.get_mini_services_by_calendar(calendar_id)
    if mini_services is None:
        raise EntityNotFoundError(Entity.CALENDAR, calendar_id)
    return mini_services


@router.get(
    "/{calendar_id}",
    response_model=Calendar,
    responses=ERROR_RESPONSES["404"],
    status_code=status.HTTP_200_OK,
)
async def get(
    service: Annotated[CalendarService, Depends(CalendarService)],
    calendar_id: Annotated[str, Path()],
    include_removed: bool = Query(False),
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
        raise EntityNotFoundError(Entity.CALENDAR, calendar_id)
    return calendar


@router.get(
    "/google/importable",
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def google_calendars_available_for_import(
    service: Annotated[CalendarService, Depends(CalendarService)],
    google_calendar_service: Annotated[
        GoogleCalendarService,
        Depends(GoogleCalendarService),
    ],
    user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """
    List Google calendars that the authenticated user owns but are not yet added to the system.

    This includes all non-primary calendars where the user has 'owner' access and
    that are not already stored in the local database.

    :param service: Calendar service.
    :param google_calendar_service: Google Calendar service.
    :param user: User who make this request.

    :returns List of importable Google Calendar entries.
    """
    google_calendars = await google_calendar_service.get_all_calendars()

    calendars = await service.google_calendars_available_for_import(user, google_calendars)
    if calendars is None:
        raise BaseAppError()
    return calendars


@router.post(
    "/",
    response_model=Calendar,
    responses=ERROR_RESPONSES["400_401_403_404"],
    status_code=status.HTTP_201_CREATED,
)
async def create(
    service: Annotated[CalendarService, Depends(CalendarService)],
    google_calendar_service: Annotated[
        GoogleCalendarService,
        Depends(GoogleCalendarService),
    ],
    user: Annotated[User, Depends(get_current_user)],
    calendar_create: CalendarCreate,
) -> Any:
    """
    Create calendar, only users with special roles can create calendar.

    :param service: Calendar service.
    :param google_calendar_service: Google Calendar service.
    :param user: User who make this request.
    :param calendar_create: Calendar Create schema.

    :returns CalendarModel: the created calendar.
    """
    if calendar_create.id:
        await google_calendar_service.user_has_calendar_access(calendar_create.id)
    else:
        calendar_create.id = (
            await google_calendar_service.create_calendar(
                calendar_create.reservation_type,
            )
        ).id

    calendar = await service.create_calendar(calendar_create, user)
    if not calendar:
        raise BaseAppError()
    return calendar


@router.post(
    "/batch",
    response_model=list[Calendar],
    responses=ERROR_RESPONSES["400_401_403_404"],
    status_code=status.HTTP_201_CREATED,
)
async def create_multiple(
    service: Annotated[CalendarService, Depends(CalendarService)],
    google_calendar_service: Annotated[
        GoogleCalendarService,
        Depends(GoogleCalendarService),
    ],
    user: Annotated[User, Depends(get_current_user)],
    calendars_create: list[CalendarCreate],
) -> Any:
    """
    Create calendars, only users with special roles can create calendar.

    :param service: Calendar service.
    :param google_calendar_service: Google Calendar service.
    :param user: User who make this request.
    :param calendars_create: Calendars Create schema.

    :returns CalendarModel: the created calendar.
    """
    calendars_result: list[Calendar] = []
    for calendar in calendars_create:
        calendars_result.append(
            await create(service, google_calendar_service, user, calendar),
        )

    return calendars_result


@router.put(
    "/{calendar_id}",
    response_model=Calendar,
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def update(
    service: Annotated[CalendarService, Depends(CalendarService)],
    user: Annotated[User, Depends(get_current_user)],
    calendar_id: Annotated[str, Path()],
    calendar_update: Annotated[CalendarUpdate, Body()],
) -> Any:
    """
    Update calendar with id equal to calendar_id, only users with special roles can update calendar.

    :param service: Calendar service.
    :param user: User who make this request.
    :param calendar_id: id of the calendar.
    :param calendar_update: CalendarUpdate schema.

    :returns CalendarModel: the updated calendar.
    """
    calendar = await service.update_calendar(calendar_id, calendar_update, user)
    if not calendar:
        raise EntityNotFoundError(Entity.CALENDAR, calendar_id)
    return calendar


@router.put(
    "/{calendar_id}/restore",
    response_model=Calendar,
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def restore(
    service: Annotated[CalendarService, Depends(CalendarService)],
    user: Annotated[User, Depends(get_current_user)],
    calendar_id: Annotated[str, Path()],
) -> Any:
    """
    Retrieve deleted calendar with uuid equal to 'calendar_id'.

    Only users with special roles can update the calendar.

    :param service: Reservation Service ser.
    :param user: User who make this request.
    :param calendar_id: id of the calendar.

    :returns CalendarModel: the updated calendar.
    """
    calendar = await service.retrieve_removed_object(calendar_id, user)
    if not calendar:
        raise EntityNotFoundError(Entity.MINI_SERVICE, calendar_id)
    return calendar


@router.delete(
    "/{calendar_id}",
    response_model=Calendar,
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def delete_calendar(
    service: Annotated[CalendarService, Depends(CalendarService)],
    user: Annotated[User, Depends(get_current_user)],
    calendar_id: Annotated[str, Path()],
    hard_remove: bool = Query(False),
) -> Any:
    """
    Delete calendar with id equal to calendar_id, only users with special roles can delete calendar.

    :param service: Calendar service.
    :param user: User who make this request.
    :param calendar_id: id of the calendar.
    :param hard_remove: hard remove of the calendar or not.

    :returns CalendarModel: the deleted calendar.
    """
    calendar = await service.delete_calendar(calendar_id, user, hard_remove)
    if not calendar:
        raise EntityNotFoundError(Entity.CALENDAR, calendar_id)
    return calendar
