"""API controllers for well known."""

from domain.schemas import WellKnownResponse
from fastapi import APIRouter, status

router = APIRouter()


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
)
async def live() -> WellKnownResponse:
    """
    Liveness probe.

    Used to verify that the application process is running.
    """
    return WellKnownResponse(status="Ok")


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
)
async def ready() -> WellKnownResponse:
    """
    Readiness probe.

    Used to determine whether the application is ready to accept incoming requests.
    """
    return WellKnownResponse(status="Ok")
