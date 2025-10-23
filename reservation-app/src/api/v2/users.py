"""API controllers for users."""

import logging
from typing import Annotated

from api import get_current_user
from core.application.exceptions import (
    ERROR_RESPONSES,
    PermissionDeniedError,
)
from core.schemas import UserLite
from core.schemas.event import EventDetail, EventTimeline
from fastapi import APIRouter, Depends, FastAPI, Query, status
from services import UserService

logger = logging.getLogger(__name__)

app = FastAPI()

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserLite],
    responses=ERROR_RESPONSES["401_403"],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    service: Annotated[UserService, Depends(UserService)],
    user: Annotated[UserLite, Depends(get_current_user)],
):
    """
    Retrieve all users from the database.

    This endpoint is accessible only to users with the 'section_head' role.
    It returns a list of all registered users.
    """
    logger.info("User %s requested list of all users.", user.id)

    if not user.section_head:
        logger.warning("Permission denied for user %s (not section_head).", user.id)
        raise PermissionDeniedError("Permission Denied.")

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
    service: Annotated[UserService, Depends(UserService)],
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


@router.get(
    "/me/events-timeline",
    response_model=EventTimeline,
    responses=ERROR_RESPONSES["400_404"],
    status_code=status.HTTP_200_OK,
)
async def get_events_by_user_filter_past_and_upcoming(
    service: Annotated[UserService, Depends(UserService)],
    user: Annotated[UserLite, Depends(get_current_user)],
):
    """Retrieve the user's events, grouped into past and upcoming."""
    return await service.get_events_by_user_filter_past_and_upcoming(user)
