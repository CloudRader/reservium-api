"""API controllers for mini services."""

from typing import Annotated, Any

from api.api_base import BaseCRUDRouter
from core.application.exceptions import (
    ERROR_RESPONSES,
    Entity,
)
from core.schemas import MiniService, MiniServiceCreate, MiniServiceUpdate
from fastapi import APIRouter, Depends, Path, Query, status
from services import MiniServiceService

router = APIRouter()


class MiniServiceRouter(
    BaseCRUDRouter[
        MiniServiceCreate,
        MiniServiceUpdate,
        MiniService,
        MiniServiceService,
    ]
):
    """
    API router for managing Mini Services.

    This class extends `BaseCRUDRouter` to automatically register standard
    CRUD routes for the `MiniService` entity and adds custom endpoints
    specific to Mini Services.
    """

    def __init__(self):
        super().__init__(
            router=router,
            service_dep=MiniServiceService,
            schema_create=MiniServiceCreate,
            schema_update=MiniServiceUpdate,
            schema=MiniService,
            entity_name=Entity.MINI_SERVICE,
        )

        self.register_routes()

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
            return await self._handle_not_found(mini_service, name)


MiniServiceRouter()
