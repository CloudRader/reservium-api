"""API controllers for mini services."""

from typing import Annotated, Any

from api import (
    ERROR_RESPONSES,
    Entity,
    EntityNotFoundError,
)
from api.api_base import BaseCRUDRouter
from core.schemas import MiniService, MiniServiceCreate, MiniServiceUpdate
from fastapi import APIRouter, Depends, Path, Query, status
from services import MiniServiceService

router = APIRouter()

crud_router = BaseCRUDRouter(
    router=router,
    service_dep=MiniServiceService,
    schema_create=MiniServiceCreate,
    schema_update=MiniServiceUpdate,
    schema=MiniService,
    entity_name=Entity.MINI_SERVICE,
)

crud_router.register_routes()


@router.get(
    "/name/{name}",
    response_model=MiniService,
    responses=ERROR_RESPONSES["404"],
    status_code=status.HTTP_200_OK,
)
async def get_by_name(
    service: Annotated[MiniServiceService, Depends(MiniServiceService)],
    name: Annotated[str, Path()],
    include_removed: bool = Query(False),
) -> Any:
    """
    Get mini service by its name.

    :param service: Mini Service ser.
    :param name: name of the mini service.
    :param include_removed: include removed mini service or not.

    :return: Mini Service with name equal to name
             or None if no such mini service exists.
    """
    mini_service = await service.get_by_name(name, include_removed)
    if not mini_service:
        raise EntityNotFoundError(Entity.MINI_SERVICE, name)
    return mini_service
