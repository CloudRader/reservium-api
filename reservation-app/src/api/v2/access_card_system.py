"""API controllers for authorisation in access card system."""

from typing import Annotated, Any

from core.application.exceptions import ERROR_RESPONSES
from core.schemas import (
    ClubAccessSystemRequest,
)
from fastapi import APIRouter, Depends, status
from services import AccessCardSystemService, EventService

router = APIRouter()


@router.post(
    "/external-authorize",
    responses=ERROR_RESPONSES["403"],
    status_code=status.HTTP_201_CREATED,
)
async def reservation_access_authorize(
    service: Annotated[AccessCardSystemService, Depends(AccessCardSystemService)],
    event_service: Annotated[EventService, Depends(EventService)],
    access_request: ClubAccessSystemRequest,
) -> Any:
    """
    Endpoint for external access authorization.

    This endpoint receives an access request from the club access control system
    containing a user's UID, room ID, and device ID. It checks whether the user has
    a valid reservation and is authorized to access the specified room and device
    at the current time.

    :param service: AccessCardSystemService instance used for authorization logic.
    :param event_service: EventService for querying reservation data.
    :param access_request: Incoming request with UID, room ID, and device ID.

    :return: Boolean result indicating whether access is granted.
    """
    return await service.reservation_access_authorize(event_service, access_request)
