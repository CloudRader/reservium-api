"""Module for authenticator functions."""

from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from integrations.information_system import IsService
from services import UserService

http_bearer = HTTPBearer()


async def authenticate_user(
    user_service: Annotated[UserService, Depends(UserService)],
    is_service: Annotated[IsService, Depends(IsService)],
    token: str,
):
    """
    Authenticate a user using their tokens from IS.

    :param user_service: UserLite service
    :param is_service: IsService service.
    :param token: Token for user identification.

    :return: The authenticated user object if successful, otherwise Exception.
    """
    user_data = await is_service.get_user_data(token)
    roles = await is_service.get_roles_data(token)
    services = await is_service.get_services_data(token)
    room = await is_service.get_room_data(token)
    return await user_service.create_user(user_data, roles, services, room)


async def get_current_user(
    user_service: Annotated[UserService, Depends(UserService)],
    is_service: Annotated[IsService, Depends(IsService)],
    token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> Any:
    """
    Retrieve the current user based on a JWT token.

    :param user_service: UserLite service.
    :param is_service: IsService service.
    :param token: The authorization token.

    :return: UserLite object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    user_data = await is_service.get_user_data(token.credentials)
    user = await user_service.get(user_data.id)

    if not user:
        raise credentials_exception
    return user
