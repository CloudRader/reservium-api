"""Root API router that includes all versioned API routers."""

from api.v1 import router as router_v1
from fastapi import APIRouter

router = APIRouter()

router.include_router(router_v1)
