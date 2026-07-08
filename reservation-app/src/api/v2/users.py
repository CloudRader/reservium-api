"""API controllers for users."""

import logging
from typing import Annotated

from api.dependencies import get_current_user, get_user_service
from api.permissions import require_permission
from api.schemas import UserLite
from api.schemas.event import EventDetail
from application.services import UserService
from core.bootstrap.exceptions import ERROR_RESPONSES
from fastapi import APIRouter, Depends, FastAPI, Query, status

logger = logging.getLogger(__name__)

app = FastAPI()

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserLite],
    responses=ERROR_RESPONSES["401_403"],
    dependencies=[Depends(require_permission("users.read"))],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[UserLite, Depends(get_current_user)],
):
    """
    Retrieve all users from the database.

    This endpoint is accessible only to users with the users.read permission.
    It returns a list of all registered users.
    """
    logger.info("User %s requested list of all users.", user.id)

    users = await service.get_all()

    logger.info("Returned %d users for section head %s.", len(users), user.id)
    return users


@router.get(
    "/me",
    response_model=UserLite,
    responses=ERROR_RESPONSES["401"],
    status_code=status.HTTP_200_OK,
)
async def get_me(
    user: Annotated[UserLite, Depends(get_current_user)],
):
    """Get currently authenticated user."""
    logger.debug("Returning profile for user %s.", user.id)
    return user


@router.get(
    "/me/events",
    response_model=list[EventDetail],
    responses=ERROR_RESPONSES["400_404"],
    status_code=status.HTTP_200_OK,
)
async def get_events_by_user(
    service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[UserLite, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="Page number for pagination. Starts at 1."),
    limit: int = Query(
        20, ge=1, le=100, description="Number of events per page (pagination limit)."
    ),
    past: bool | None = Query(
        None,
        description="Filter events by time. `True` for past events, `False` for future events, "
        "`None` for all events.",
    ),
):
    """Get events linked to a user by its ID."""
    logger.info(
        "User %s requested events (page=%s, limit=%s, past=%s).", user.id, page, limit, past
    )
    return await service.get_events_by_user(user, page, limit, past)
