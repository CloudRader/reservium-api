"""Root API router that includes all versioned API routers."""

from api.v2 import router as router_v2
from api.well_known import router as router_well_known
from core.bootstrap.docs import fastapi_docs
from fastapi import APIRouter

router = APIRouter()

router.include_router(
    router_well_known,
    prefix="/well-known",
    tags=[fastapi_docs.WELL_KNOWN_TAG["name"]],
)

router.include_router(router_v2)
