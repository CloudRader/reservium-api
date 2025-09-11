"""API controllers for users."""

from typing import Annotated, Any

from api import get_current_user
from core.application.exceptions import (
    ERROR_RESPONSES,
    BaseAppError,
    PermissionDeniedError,
)
from core.schemas import UserLite
from core.schemas.event import EventDetail, EventTimeline
from fastapi import APIRouter, Depends, FastAPI, status
from services import UserService

app = FastAPI()

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserLite],
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    service: Annotated[UserService, Depends(UserService)],
    user: Annotated[UserLite, Depends(get_current_user)],
) -> Any:
    """
    Retrieve all users from the database.

    This endpoint is accessible only to users with the 'section_head' role.
    It returns a list of all registered users.

    :param service: UserLite service.
    :param user: UserLite who make this request.

    :return: All users in database.
    """
    if not user.section_head:
        raise PermissionDeniedError("Permission Denied.")

    users = await service.get_all()
    if users is None:
        raise BaseAppError()
    return users


@router.get(
    "/me",
    response_model=UserLite,
    responses=ERROR_RESPONSES["401"],
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: Annotated[UserLite, Depends(get_current_user)],
) -> Any:
    """
    Get currently authenticated user.

    :param current_user: Current user.

    :return: Current user.
    """
    return current_user


@router.get(
    "/me/events",
    response_model=list[EventDetail],
    responses=ERROR_RESPONSES["400_404"],
    status_code=status.HTTP_200_OK,
)
async def get_events_by_user(
    service: Annotated[UserService, Depends(UserService)],
    user: Annotated[UserLite, Depends(get_current_user)],
) -> Any:
    """
    Get all events linked to a user by its ID.

    :param service: User service.
    :param user: UserLite who make this request.

    :return: List of EventWithExtraDetails objects linked to the user.
    """
    return await service.get_events_by_user(user)


@router.get(
    "/me/events-timeline",
    response_model=EventTimeline,
    responses=ERROR_RESPONSES["400_404"],
    status_code=status.HTTP_200_OK,
)
async def get_events_by_user_filter_past_and_upcoming(
    service: Annotated[UserService, Depends(UserService)],
    user: Annotated[UserLite, Depends(get_current_user)],
) -> Any:
    """
    Retrieve the user's events, grouped into past and upcoming.

    :param service: User service.
    :param user: UserLite who make this request.

    :return: Dictionary with two lists of events:
             - ``past``: events that have already ended,
             - ``upcoming``: events that are scheduled in the future.
    """
    return await service.get_events_by_user_filter_past_and_upcoming(user)
