"""Root API router that includes all versioned API routers."""

from api.v2 import router as router_v2
from fastapi import APIRouter

router = APIRouter()

router.include_router(router_v2)
