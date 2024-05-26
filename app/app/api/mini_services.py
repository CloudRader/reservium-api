"""
API controllers for mini services.
"""
from typing import Any, Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, Path, status, Body
from fastapi.responses import JSONResponse

from api import EntityNotFoundException, Entity, Message, fastapi_docs
from schemas import MiniServiceCreate, MiniServiceUpdate, MiniService
from services import MiniServiceService, UserService

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
async def create_mini_service(service: Annotated[MiniServiceService, Depends(MiniServiceService)],
                              user_service: Annotated[UserService, Depends(UserService)],
                              mini_service_create: MiniServiceCreate,
                              username: str) -> Any:
    """
    Create mini service, only users with special roles can create mini service.

    :param service: Mini Service ser.
    :param user_service: User service.
    :param mini_service_create: Mini Service Create schema.
    :param username: Username of the user who will make this request.

    :returns MiniServiceModel: the created mini service.
    """
    user = user_service.get_by_username(username)
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


@router.get("/{mini_service_uuid}",
            response_model=MiniService,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_mini_service(service: Annotated[MiniServiceService, Depends(MiniServiceService)],
                           mini_service_uuid: Annotated[str, Path()]) -> Any:
    """
    Get mini service by its uuid.

    :param service: Mini Service ser.
    :param mini_service_uuid: uuid of the mini service.

    :return: Mini Service with uuid equal to uuid
             or None if no such mini service exists.
    """
    mini_service = service.get(mini_service_uuid)
    if not mini_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, mini_service_uuid)
    return mini_service


@router.get("/",
            response_model=List[MiniService],
            status_code=status.HTTP_200_OK)
async def get_mini_services(service: Annotated[MiniServiceService, Depends(MiniServiceService)]
                            ) -> Any:
    """
    Get all mini services from database.

    :param service: Mini Service ser.

    :return: List of all mini services or None if there are no mini services in db.
    """
    mini_services = service.get_all()
    if not mini_services:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "No mini services in db."
            }
        )
    return mini_services


@router.put("/{mini_service_uuid}",
            response_model=MiniService,
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def update_mini_service(service: Annotated[MiniServiceService, Depends(MiniServiceService)],
                              user_service: Annotated[UserService, Depends(UserService)],
                              mini_service_uuid: Annotated[UUID, Path()],
                              mini_service_update: Annotated[MiniServiceUpdate, Body()],
                              username: str) -> Any:
    """
    Update mini service with uuid equal to mini_service_uuid,
    only users with special roles can update mini service.

    :param service: Mini Service ser.
    :param user_service: User service.
    :param mini_service_uuid: uuid of the mini service.
    :param mini_service_update: MiniServiceUpdate schema.
    :param username: Username of the user who will make this request.

    :returns MiniServiceModel: the updated mini service.
    """
    user = user_service.get_by_username(username)
    mini_service = service.update_mini_service(mini_service_uuid, mini_service_update, user)
    if not mini_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, mini_service_uuid)
    return mini_service


@router.delete("/{mini_service_uuid}",
               response_model=MiniService,
               responses={
                   **EntityNotFoundException.RESPONSE,
               },
               status_code=status.HTTP_200_OK)
async def delete_mini_service(service: Annotated[MiniServiceService, Depends(MiniServiceService)],
                              user_service: Annotated[UserService, Depends(UserService)],
                              mini_service_uuid: Annotated[UUID, Path()],
                              username: str) -> Any:
    """
    Delete calendar with id equal to calendar_id,
    only users with special roles can delete mini service.

    :param service: Mini Service ser.
    :param user_service: User service.
    :param mini_service_uuid: uuid of the mini service.
    :param username: Username of the user who will make this request.

    :returns MiniServiceModel: the deleted mini service.
    """
    user = user_service.get_by_username(username)
    mini_service = service.delete_mini_service(mini_service_uuid, user)
    if not mini_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, mini_service_uuid)
    return mini_service


@router.get("/alias/{service_alias}",
            response_model=List[MiniService],
            responses={
                **EntityNotFoundException.RESPONSE,
            },
            status_code=status.HTTP_200_OK)
async def get_mini_services_by_alias(service: Annotated[MiniServiceService,
                                     Depends(MiniServiceService)],
                                     service_alias: Annotated[str, Path()]) -> Any:
    """
    Get mini services by its service alias.

    :param service: Mini Service ser.
    :param service_alias: service alias of the mini service.

    :return: Mini Service with uuid equal to uuid
             or None if no such mini service exists.
    """
    mini_service = service.get_by_service_alias(service_alias)
    if not mini_service:
        raise EntityNotFoundException(Entity.MINI_SERVICE, service_alias)
    return mini_service
