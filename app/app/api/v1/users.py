"""
API controllers for users.
"""

from typing import Annotated, Any

from api import (
    fastapi_docs,
    get_current_user,
)
from core.schemas import User
from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.responses import JSONResponse
from services import UserService

app = FastAPI()

router = APIRouter(tags=[fastapi_docs.USER_TAG["name"]])


@router.get("/me", response_model=User)
async def get_user(current_user: Annotated[User, Depends(get_current_user)]) -> Any:
    """
    Get currently authenticated user.

    :param current_user: Current user.

    :return: Current user.
    """
    return current_user


@router.get(
    "/",
    response_model=list[User],
    # responses=ERROR_RESPONSES["404"],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    user_service: Annotated[UserService, Depends(UserService)],
) -> Any:
    """
    Get all users.

    :param user_service: User service.

    :return: All users in database.
    """
    users = await user_service.get_all()
    if not users:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "No users in db."},
        )
    return users
