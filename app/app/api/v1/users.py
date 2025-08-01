"""API controllers for users."""

from typing import Annotated, Any

from api import (
    ERROR_RESPONSES,
    BaseAppError,
    PermissionDeniedError,
    fastapi_docs,
    get_current_user,
)
from core.schemas import EventWithExtraDetails, User
from fastapi import APIRouter, Depends, FastAPI, status
from services import UserService

app = FastAPI()

router = APIRouter(tags=[fastapi_docs.USER_TAG["name"]])


@router.get(
    "/",
    response_model=list[User],
    responses=ERROR_RESPONSES["400_401_403"],
    status_code=status.HTTP_200_OK,
)
async def get_all(
    service: Annotated[UserService, Depends(UserService)],
    user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """
    Retrieve all users from the database.

    This endpoint is accessible only to users with the 'section_head' role.
    It returns a list of all registered users.

    :param service: User service.
    :param user: User who make this request.

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
    response_model=User,
    responses=ERROR_RESPONSES["401"],
    status_code=status.HTTP_200_OK,
)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> Any:
    """
    Get currently authenticated user.

    :param current_user: Current user.

    :return: Current user.
    """
    return current_user


@router.get(
    "/me/events",
    response_model=list[EventWithExtraDetails],
    responses=ERROR_RESPONSES["400_404"],
    status_code=status.HTTP_200_OK,
)
async def get_events_by_user(
    service: Annotated[UserService, Depends(UserService)],
    user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """
    Get all events linked to a user by its ID.

    :param service: User service.
    :param user: User who make this request.

    :return: List of EventWithExtraDetails objects linked to the user.
    """
    events = await service.get_events_by_user_id(user)
    if events is None:
        raise BaseAppError()
    return events
