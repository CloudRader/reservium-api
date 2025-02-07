"""
API controllers for mini services.
"""
from typing import Any, Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, Path, status, Body, Query
from fastapi.responses import JSONResponse

from api import EntityNotFoundException, Entity, Message, fastapi_docs, \
    get_current_user
from schemas import MiniServiceCreate, MiniServiceUpdate, MiniService, User
from services import MiniServiceService

router = APIRouter(
    prefix='/mini_services',
    tags=[fastapi_docs.MINI_SERVICE_TAG["name"]]
)


@router.post("/create_mini_service",
             response_model=MiniService,
             responses={
                 400: {"model": Message,
                       "description": "Couldn't create mini service."},
             },
             status_code=status.HTTP_201_CREATED)
async def create_mini_service(
        service: Annotated[MiniServiceService, Depends(MiniServiceService)],
        user: Annotated[User, Depends(get_current_user)],
        mini_service_create: MiniServiceCreate
) -> Any:
    """
    Create mini service, only users with special roles can create mini service.

    :param service: Mini Service ser.
    :param user: User who make this request.
    :param mini_service_create: Mini Service Create schema.

    :returns MiniServiceModel: the created mini service.
    """
    mini_service = service.create_mini_service(mini_service_create, user)
    if not mini_service:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Could not create mini services, because bad "
                           "request or you don't have permission for that."
            }
        )
    return mini_service


@router.post("/create_mini_services",
             response_model=List[MiniService],
             responses={
                 400: {"model": Message,
                       "description": "Couldn't create mini service."},
             },
             status_code=status.HTTP_201_CREATED)
async def create_mini_services(
        service: Annotated[MiniServiceService, Depends(MiniServiceService)],
        user: Annotated[User, Depends(get_current_user)],
        mini_services_create: List[MiniServiceCreate]
) -> Any:
    """
    Create mini services, only users with special roles can create mini service.

    :param service: Mini Service ser.
    :param user: User who make this request.
    :param mini_services_create: Mini Services Create schema.

    :returns MiniServiceModel: the created mini service.
    """
    mini_service_result: List[MiniService] = []
    for mini_service_create in mini_services_create:
        mini_service_result.append(
            await create_mini_service(service, user, mini_service_create)
        )

    return mini_service_result


@router.get("/{mini_service_id}",
            response_model=MiniService,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_mini_service(
        service: Annotated[MiniServiceService, Depends(MiniServiceService)],
        mini_service_id: Annotated[str, Path()],
        include_removed: bool = Query(False)
) -> Any:
    """
    Get mini service by its uuid.

    :param service: Mini Service ser.
    :param mini_service_id: uuid of the mini service.
    :param include_removed: include removed mini service or not.

    :return: Mini Service with uuid equal to uuid
             or None if no such mini service exists.
    """
    mini_service = service.get(mini_service_id, include_removed)
    if not mini_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, mini_service_id)
    return mini_service


@router.get("/",
            response_model=List[MiniService],
            status_code=status.HTTP_200_OK)
async def get_mini_services(
        service: Annotated[MiniServiceService, Depends(MiniServiceService)],
        include_removed: bool = Query(False)
) -> Any:
    """
    Get all mini services from database.

    :param service: Mini Service ser.
    :param include_removed: include removed mini services or not.

    :return: List of all mini services or None if there are no mini services in db.
    """
    mini_services = service.get_all(include_removed)
    if not mini_services:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "No mini services in db."
            }
        )
    return mini_services


@router.put("/{mini_service_id}",
            response_model=MiniService,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def update_mini_service(
        service: Annotated[MiniServiceService, Depends(MiniServiceService)],
        user: Annotated[User, Depends(get_current_user)],
        mini_service_id: Annotated[UUID, Path()],
        mini_service_update: Annotated[MiniServiceUpdate, Body()]
) -> Any:
    """
    Update mini service with uuid equal to mini_service_uuid,
    only users with special roles can update mini service.

    :param service: Mini Service ser.
    :param user: User who make this request.
    :param mini_service_id: uuid of the mini service.
    :param mini_service_update: MiniServiceUpdate schema.

    :returns MiniServiceModel: the updated mini service.
    """
    mini_service = service.update_mini_service(mini_service_id, mini_service_update, user)
    if not mini_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, mini_service_id)
    return mini_service


@router.delete("/{mini_service_id}",
               response_model=MiniService,
               responses={
                   **EntityNotFoundException.RESPONSE,
               },
               status_code=status.HTTP_200_OK)
async def delete_mini_service(
        service: Annotated[MiniServiceService, Depends(MiniServiceService)],
        user: Annotated[User, Depends(get_current_user)],
        mini_service_id: Annotated[UUID, Path()],
        hard_remove: bool = Query(False)
) -> Any:
    """
    Delete mini service with mini_service_uuid equal to uuid,
    only users with special roles can delete mini service.

    :param service: Mini Service ser.
    :param user: User who make this request.
    :param mini_service_id: uuid of the mini service.
    :param hard_remove: hard remove of the mini service or not.

    :returns MiniServiceModel: the deleted mini service.
    """
    mini_service = service.delete_mini_service(mini_service_id, user,
                                               hard_remove)
    if not mini_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, mini_service_id)
    return mini_service


@router.get("/name/{name}",
            response_model=MiniService,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_mini_services_by_name(
        service: Annotated[MiniServiceService, Depends(MiniServiceService)],
        name: Annotated[str, Path()],
        include_removed: bool = Query(False)
) -> Any:
    """
    Get mini service by its name.

    :param service: Mini Service ser.
    :param name: name of the mini service.
    :param include_removed: include removed mini service or not.

    :return: Mini Service with name equal to name
             or None if no such mini service exists.
    """
    mini_service = service.get_by_name(name, include_removed)
    if not mini_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, name)
    return mini_service


@router.get("/reservation_service/{reservation_service_id}",
            response_model=List[MiniService],
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_mini_services_by_reservation_service_id(
        service: Annotated[MiniServiceService, Depends(MiniServiceService)],
        reservation_service_id: Annotated[str, Path()],
        include_removed: bool = Query(False)
) -> Any:
    """
    Get mini services by its reservation service id.

    :param service: Mini Service ser.
    :param reservation_service_id: reservation service id of the mini services.
    :param include_removed: include removed mini service or not.

    :return: Mini Services with reservation service id equal
    to reservation service id or None if no such mini services exists.
    """
    mini_services = service.get_by_reservation_service_id(reservation_service_id,
                                                         include_removed)
    if not mini_services:
        raise EntityNotFoundException(Entity.MINI_SERVICE, reservation_service_id)
    return mini_services
