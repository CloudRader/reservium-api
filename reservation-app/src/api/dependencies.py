"""Module for authenticator functions."""

import logging
from typing import Annotated, Any

from core.schemas.keycloak import CurrentUser
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from integrations.keycloak import KeycloakAuthService
from services import UserService

logger = logging.getLogger(__name__)

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

    :return: User object.
    """
    logger.debug("Retrieving current user from token.")
    user_keycloak = await keycloak_service.get_user_info(token.credentials)

    return await user_service.get(user_keycloak.ldap_id)


async def get_current_user_from_token(
    keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
    token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> Any:
    """
    Retrieve the current user based on a JWT token.

    :param keycloak_service: IsService service.
    :param token: The authorization token.

    :return: User object.
    """
    logger.debug("Retrieving current user from token test.")
    decoded_token = await keycloak_service.decode_token(token.credentials)

    return CurrentUser.from_token(
        decoded_token,
        decoded_token["azp"],
    )
