"""Module for authenticator functions."""

from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from integrations.keycloak import KeycloakAuthService
from services import UserService

http_bearer = HTTPBearer()


async def get_current_user(
    user_service: Annotated[UserService, Depends(UserService)],
    keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
    token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> Any:
    """
    Retrieve the current user based on a JWT token.

    :param user_service: UserLite service.
    :param keycloak_service: IsService service.
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

    user_data = await keycloak_service.get_user_info(token.credentials)
    user = await user_service.get(user_data.ldap_id)

    if not user:
        raise credentials_exception
    return user
