"""
Root API router that includes all versioned API routers.
"""

from fastapi import APIRouter
from api.v1 import router as router_v1


router = APIRouter()

router.include_router(router_v1)
