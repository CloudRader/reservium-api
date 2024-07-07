"""
API controllers for reservation services.
"""
from typing import Any, Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, Path, status, Body
from fastapi.responses import JSONResponse

from api import EntityNotFoundException, Entity, Message, fastapi_docs, \
    get_current_user
from schemas import ReservationServiceCreate, ReservationServiceUpdate, ReservationService, User
from services import ReservationServiceService

router = APIRouter(
    prefix='/reservation_services',
    tags=[fastapi_docs.RESERVATION_SERVICE_TAG["name"]]
)


@router.post("/create_reservation_service",
             response_model=ReservationService,
             responses={
                 400: {"model": Message,
                       "description": "Couldn't create reservation service."},
             },
             status_code=status.HTTP_201_CREATED)
async def create_reservation_service(
        service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
        user: Annotated[User, Depends(get_current_user)],
        reservation_service_create: ReservationServiceCreate
) -> Any:
    """
    Create reservation service, only user with head of the
    operation section role can create reservation service.

    :param service: Reservation Service ser.
    :param user: User who make this request.
    :param reservation_service_create: Reservation Service Create schema.

    :returns ReservationServiceModel: the created reservation service.
    """
    reservation_service = service.create_reservation_service(
        reservation_service_create, user
    )
    if not reservation_service:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Could not create reservation services, because bad "
                           "request or you don't have permission for that."
            }
        )
    return reservation_service


@router.get("/{reservation_service_uuid}",
            response_model=ReservationService,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_reservation_service(
        service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
        reservation_service_uuid: Annotated[str, Path()]
) -> Any:
    """
    Get reservation service by its uuid.

    :param service: Reservation Service ser.
    :param reservation_service_uuid: uuid of the reservation service.

    :return: Reservation Service with uuid equal to uuid
             or None if no such reservation service exists.
    """
    reservation_service = service.get(reservation_service_uuid)
    if not reservation_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, reservation_service_uuid)
    return reservation_service


@router.get("/",
            response_model=List[ReservationService],
            status_code=status.HTTP_200_OK)
async def get_reservation_services(
        service: Annotated[ReservationServiceService, Depends(ReservationServiceService)]
) -> Any:
    """
    Get all reservation services from database.

    :param service: Reservation Service ser.

    :return: List of all reservation services or None if there are no reservation services in db.
    """
    reservation_service = service.get_all()
    if not reservation_service:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "No reservation services in db."
            }
        )
    return reservation_service


@router.put("/{reservation_service_uuid}",
            response_model=ReservationService,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def update_reservation_service(
        service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
        user: Annotated[User, Depends(get_current_user)],
        reservation_service_uuid: Annotated[UUID, Path()],
        reservation_service_update: Annotated[ReservationServiceUpdate, Body()]
) -> Any:
    """
    Update reservation service with uuid equal to reservation_service_uuid,
    only user with head of the operation section role can update reservation service.

    :param service: Reservation Service ser.
    :param user: User who make this request.
    :param reservation_service_uuid: uuid of the reservation service.
    :param reservation_service_update: ReservationServiceUpdate schema.

    :returns ReservationServiceModel: the updated reservation service.
    """
    reservation_service = service.update_mini_service(
        reservation_service_uuid, reservation_service_update, user
    )
    if not reservation_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, reservation_service_uuid)
    return reservation_service


@router.delete("/{reservation_service_uuid}",
               response_model=ReservationService,
               responses={
                   **EntityNotFoundException.RESPONSE,
               },
               status_code=status.HTTP_200_OK)
async def delete_reservation_service(
        service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
        user: Annotated[User, Depends(get_current_user)],
        reservation_service_uuid: Annotated[UUID, Path()],
) -> Any:
    """
    Delete reservation service with id equal to reservation_service_uuid,
    only user with head of the operation section role can delete reservation service.

    :param service: Reservation Service ser.
    :param user: User who make this request.
    :param reservation_service_uuid: uuid of the reservation service.

    :returns ReservationServiceModel: the deleted reservation service.
    """
    reservation_service = service.delete_mini_service(reservation_service_uuid, user)
    if not reservation_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, reservation_service_uuid)
    return reservation_service


@router.get("/name/{name}",
            response_model=ReservationService,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_reservation_service_by_name(
        service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
        name: Annotated[str, Path()]
) -> Any:
    """
    Get reservation services by its name.

    :param service: Mini Service ser.
    :param name: service alias of the mini service.

    :return: Reservation Service with name equal to name
             or None if no such reservation service exists.
    """
    reservation_service = service.get_by_name(name)
    if not reservation_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, name)
    return reservation_service


@router.get("/alias/{alias}",
            response_model=ReservationService,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_reservation_service_by_alias(
        service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
        alias: Annotated[str, Path()]
) -> Any:
    """
    Get reservation services by its alias.

    :param service: Mini Service ser.
    :param alias: service alias of the mini service.

    :return: Reservation Service with alias equal to alias
             or None if no such reservation service exists.
    """
    reservation_service = service.get_by_alias(alias)
    if not reservation_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, alias)
    return reservation_service
