"""Module for authenticator functions."""

import logging
from typing import Annotated, Any

from domain.schemas.openid import CurrentUser
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from integrations.openid import OpenIdProvider
from services import UserService

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer()


async def get_current_user(
    user_service: Annotated[UserService, Depends(UserService)],
    openid_service: Annotated[OpenIdProvider, Depends(OpenIdProvider)],
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
    decoded_token = await openid_service.decode_token(token.credentials)
    user_from_token = CurrentUser.from_token(
        decoded_token,
        decoded_token["azp"],
    )

    return await user_service.get_by_username(user_from_token.username)


async def get_current_user_from_token(
    openid_service: Annotated[OpenIdProvider, Depends(OpenIdProvider)],
    token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> Any:
    """
    Retrieve the current user based on a JWT token.

    :param keycloak_service: IsService service.
    :param token: The authorization token.

    :return: User object.
    """
    logger.debug("Retrieving current user from token test.")
    decoded_token = await openid_service.decode_token(token.credentials)

    return CurrentUser.from_token(
        decoded_token,
        decoded_token["azp"],
    )
