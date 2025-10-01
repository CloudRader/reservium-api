"""Module for authenticator functions."""

from typing import Annotated, Any

from core import settings
from core.application.exceptions import PermissionDeniedError
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from integrations.keycloak import KeycloakAuthService
from services import UserService

http_bearer = HTTPBearer()


def require_roles(allowed_roles: list[str]):
    """Dependency that checks if the current user has at least one of the required roles."""

    async def role_checker(
        token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
        keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
        request: Request,
    ):
        action = request["method"]
        resource = request.url.path
        token_info = await keycloak_service.decode_token(token.credentials)
        roles = token_info["resource_access"][settings.KEYCLOAK.CLIENT_ID]["roles"]
        if not any(role in roles for role in allowed_roles):
            raise PermissionDeniedError()
        return roles
    return role_checker


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

    :return: User object.
    """
    user_keycloak = await keycloak_service.get_user_info(token.credentials)
    return await user_service.get(user_keycloak.ldap_id)
