"""API controllers for reservation services."""

from typing import Annotated, Any
from uuid import UUID

from api import (
    ERROR_RESPONSES,
    BaseAppError,
    Entity,
    EntityNotFoundError,
    fastapi_docs,
    get_current_token,
    get_current_user,
)
from core.models.event import EventState
from core.schemas import (
    Calendar,
    EventWithExtraDetails,
    MiniService,
    ReservationService,
    ReservationServiceCreate,
    ReservationServiceUpdate,
    User,
)
from fastapi import APIRouter, Body, Depends, Path, Query, status
from services import ReservationServiceService, UserService

router = APIRouter(tags=[fastapi_docs.RESERVATION_SERVICE_TAG["name"]])


@router.get(
    "/",
    response_model=list[ReservationService],
    responses=ERROR_RESPONSES["400"],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    user: Annotated[User, Depends(get_current_user)],
    include_removed: bool = Query(False),
) -> Any:
    """
    Get all reservation services from database.

    :param service: Reservation Service ser.
    :param user: User who make this request.
    :param include_removed: include removed reservation service or not.

    :return: List of all reservation services or None if there are no reservation services in db.
    """
    if user.active_member:
        if include_removed:
            reservation_service = await service.get_all_services_include_all_removed()
        else:
            reservation_service = await service.get_all(include_removed)
    else:
        reservation_service = await service.get_public_services()
    if reservation_service is None:
        raise BaseAppError()
    return reservation_service


@router.get(
    "/public",
    response_model=list[ReservationService],
    responses=ERROR_RESPONSES["400"],
    status_code=status.HTTP_200_OK,
)
async def get_public(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
) -> Any:
    """
    Get all public reservation services from database.

    :param service: Reservation Service ser.

    :return: List of all public reservation services or None if
    there are no reservation services in db.
    """
    reservation_services = await service.get_public_services()
    if reservation_services is None:
        raise BaseAppError()
    return reservation_services


@router.get(
    "/name/{name}",
    response_model=ReservationService,
    responses=ERROR_RESPONSES["404"],
    status_code=status.HTTP_200_OK,
)
async def get_by_name(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    name: Annotated[str, Path()],
    include_removed: bool = Query(False),
) -> Any:
    """
    Get reservation services by its name.

    :param service: Mini Service ser.
    :param name: service alias of the mini service.
    :param include_removed: include removed reservation service or not.

    :return: Reservation Service with name equal to name
             or None if no such reservation service exists.
    """
    reservation_service = await service.get_by_name(name, include_removed)
    if not reservation_service:
        raise EntityNotFoundError(Entity.RESERVATION_SERVICE, name)
    return reservation_service


@router.get(
    "/alias/{alias}",
    response_model=ReservationService,
    responses=ERROR_RESPONSES["404"],
    status_code=status.HTTP_200_OK,
)
async def get_by_alias(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    alias: Annotated[str, Path()],
    include_removed: bool = Query(False),
) -> Any:
    """
    Get reservation services by its alias.

    :param service: Mini Service ser.
    :param alias: service alias of the mini service.
    :param include_removed: include removed reservation service or not.

    :return: Reservation Service with alias equal to alias
             or None if no such reservation service exists.
    """
    reservation_service = await service.get_by_alias(alias, include_removed)
    if not reservation_service:
        raise EntityNotFoundError(Entity.RESERVATION_SERVICE, alias)
    return reservation_service


@router.get(
    "/{reservation_service_id}",
    response_model=ReservationService,
    responses=ERROR_RESPONSES["404"],
    status_code=status.HTTP_200_OK,
)
async def get(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    reservation_service_id: Annotated[UUID, Path()],
    include_removed: bool = Query(False),
) -> Any:
    """
    Get reservation service by its uuid.

    :param service: Reservation Service ser.
    :param reservation_service_id: uuid of the reservation service.
    :param include_removed: include removed reservation service or not.

    :return: Reservation Service with uuid equal to uuid
             or None if no such reservation service exists.
    """
    reservation_service = await service.get(reservation_service_id, include_removed)
    if not reservation_service:
        raise EntityNotFoundError(Entity.RESERVATION_SERVICE, reservation_service_id)
    return reservation_service


@router.get(
    "/{alias}/calendars",
    response_model=list[Calendar],
    responses=ERROR_RESPONSES["400_404"],
    status_code=status.HTTP_200_OK,
)
async def get_calendars_by_reservation_service(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    alias: Annotated[str, Path()],
    include_removed: bool = Query(False),
) -> Any:
    """
    Get all calendars linked to a reservation service by its ID.

    :param service: Reservation Service ser.
    :param alias: alias of the reservation service.
    :param include_removed: include removed calendars or not.

    :return: List of Calendar objects linked to the reservation service.
    """
    calendars = await service.get_calendars_by_alias(alias, include_removed)
    if calendars is None:
        raise BaseAppError()
    return calendars


@router.get(
    "/{alias}/mini-services",
    response_model=list[MiniService],
    responses=ERROR_RESPONSES["400_404"],
    status_code=status.HTTP_200_OK,
)
async def get_mini_services_by_reservation_service(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    alias: Annotated[str, Path()],
    include_removed: bool = Query(False),
) -> Any:
    """
    Get all mini services linked to a reservation service by its ID.

    :param service: Reservation Service ser.
    :param alias: alias of the reservation service.
    :param include_removed: include removed calendars or not.

    :return: List of MiniService objects linked to the reservation service.
    """
    mini_services = await service.get_mini_services_by_alias(alias, include_removed)
    if mini_services is None:
        raise BaseAppError()
    return mini_services


@router.get(
    "/{alias}/events",
    response_model=list[EventWithExtraDetails],
    responses=ERROR_RESPONSES["400_404"],
    status_code=status.HTTP_200_OK,
)
async def get_events_by_reservation_service(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    alias: Annotated[str, Path()],
    event_state: Annotated[EventState | None, Query()] = None,
) -> Any:
    """
    Get all events linked to a reservation service by its alias.

    :param service: Event service.
    :param alias: alias of the reservation service.
    :param event_state: event state of the event.

    :return: List of Event objects linked to the reservation service.
    """
    events = await service.get_events_by_alias(alias, event_state)
    if events is None:
        raise BaseAppError()
    return events


@router.post(
    "/",
    response_model=ReservationService,
    response_model_exclude={"calendars", "mini_services"},
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_201_CREATED,
)
async def create(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    user_service: Annotated[UserService, Depends(UserService)],
    user: Annotated[User, Depends(get_current_user)],
    token: Annotated[Any, Depends(get_current_token)],
    reservation_service_create: ReservationServiceCreate,
) -> Any:
    """
    Create reservation service.

    Only user with head of the operation section role can create reservation service.

    :param service: Reservation Service ser.
    :param user_service: User service.
    :param user: User who make this request.
    :param token: Token for user identification.
    :param reservation_service_create: Reservation Service Create schema.

    :returns ReservationServiceModel: the created reservation service.
    """
    reservation_service = await service.create_reservation_service(
        reservation_service_create,
        user,
    )
    if not reservation_service:
        raise BaseAppError()
    return reservation_service


@router.post(
    "/batch",
    response_model=list[ReservationService],
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_201_CREATED,
)
async def create_multiple(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    user_service: Annotated[UserService, Depends(UserService)],
    user: Annotated[User, Depends(get_current_user)],
    token: Annotated[Any, Depends(get_current_token)],
    reservation_services_create: list[ReservationServiceCreate],
) -> Any:
    """
    Create reservation services.

    Only user with head of the operation section role can create reservation services.

    :param service: Reservation Service ser.
    :param user_service: User service.
    :param user: User who make this request.
    :param token: Token for user identification.
    :param reservation_services_create: Reservation Services Create schema.

    :returns ReservationServicesModel: the created reservation service.
    """
    reservation_services_result: list[ReservationService] = []
    for reservation in reservation_services_create:
        reservation_services_result.append(
            await create(
                service,
                user_service,
                user,
                token,
                reservation,
            ),
        )
    return reservation_services_result


@router.put(
    "/{reservation_service_id}",
    response_model=ReservationService,
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def update(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    user: Annotated[User, Depends(get_current_user)],
    reservation_service_id: Annotated[UUID, Path()],
    reservation_service_update: Annotated[ReservationServiceUpdate, Body()],
) -> Any:
    """
    Update reservation service with uuid equal to 'reservation_service_id'.

    Only user with head of the operation section role can update reservation service.

    :param service: Reservation Service ser.
    :param user: User who make this request.
    :param reservation_service_id: uuid of the reservation service.
    :param reservation_service_update: ReservationServiceUpdate schema.

    :returns ReservationServiceModel: the updated reservation service.
    """
    reservation_service = await service.update_reservation_service(
        reservation_service_id,
        reservation_service_update,
        user,
    )
    if not reservation_service:
        raise EntityNotFoundError(Entity.RESERVATION_SERVICE, reservation_service_id)
    return reservation_service


@router.put(
    "/{reservation_service_id}/restore",
    response_model=ReservationService,
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def restore(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    user: Annotated[User, Depends(get_current_user)],
    reservation_service_id: Annotated[UUID, Path()],
) -> Any:
    """
    Retrieve deleted reservation service with uuid equal to 'reservation_service_id'.

    Only user with head of the operation section role can update reservation service.

    :param service: Reservation Service ser.
    :param user: User who make this request.
    :param reservation_service_id: uuid of the reservation service.

    :returns ReservationServiceModel: the updated reservation service.
    """
    reservation_service = await service.retrieve_removed_object(
        reservation_service_id,
        user,
    )
    if not reservation_service:
        raise EntityNotFoundError(Entity.RESERVATION_SERVICE, reservation_service_id)
    return reservation_service


@router.delete(
    "/{reservation_service_id}",
    response_model=ReservationService,
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def delete(
    service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
    user: Annotated[User, Depends(get_current_user)],
    reservation_service_id: Annotated[UUID, Path()],
    hard_remove: bool = Query(False),
) -> Any:
    """
    Delete reservation service with id equal to 'reservation_service_id'.

    Only user with head of the operation section role can delete reservation service.

    :param service: Reservation Service ser.
    :param user: User who make this request.
    :param reservation_service_id: uuid of the reservation service.
    :param hard_remove: hard remove of the reservation service or not.

    :returns ReservationServiceModel: the deleted reservation service.
    """
    reservation_service = await service.delete_reservation_service(
        reservation_service_id,
        user,
        hard_remove,
    )
    if not reservation_service:
        raise EntityNotFoundError(Entity.RESERVATION_SERVICE, reservation_service_id)
    return reservation_service
