"""API controllers for mini services."""

import logging
from typing import Annotated, Any

from api.api_base import BaseCRUDRouter
from core.application.exceptions import (
    ERROR_RESPONSES,
    Entity,
)
from core.schemas import MiniServiceCreate, MiniServiceDetail, MiniServiceLite, MiniServiceUpdate
from fastapi import APIRouter, Depends, Path, Query, status
from services import MiniServiceService

logger = logging.getLogger(__name__)

router = APIRouter()


class MiniServiceRouter(
    BaseCRUDRouter[
        MiniServiceCreate,
        MiniServiceUpdate,
        MiniServiceLite,
        MiniServiceDetail,
        MiniServiceService,
    ]
):
    """
    API router for managing Mini Services.

    This class extends `BaseCRUDRouter` to automatically register standard
    CRUD routes for the `MiniServices` entity and adds custom endpoints
    specific to Mini Services.
    """

    def __init__(self):
        super().__init__(
            router=router,
            service_dep=MiniServiceService,
            schema_create=MiniServiceCreate,
            schema_update=MiniServiceUpdate,
            schema_lite=MiniServiceLite,
            schema_detail=MiniServiceDetail,
            entity_name=Entity.MINI_SERVICE,
        )

        self.register_routes()

        @router.get(
            "/name/{name}",
            response_model=MiniServiceDetail,
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_by_name(
            service: Annotated[MiniServiceService, Depends(MiniServiceService)],
            name: Annotated[str, Path()],
            include_removed: bool = Query(False, description="Include `removed object` or not."),
        ) -> Any:
            """Get mini service by its name."""
            logger.debug(
                "Request received: get_by_name(name=%s, include_removed=%s)",
                name,
                include_removed,
            )
            mini_service = await service.get_by_name(name, include_removed)
            logger.debug("Fetched Mini service: %s", mini_service)
            return mini_service


MiniServiceRouter()
