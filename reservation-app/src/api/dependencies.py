"""Module for authenticator functions."""

import logging
from typing import Annotated, Any

from api.schemas.current_user import CurrentUser
from application.ports.providers.identity.provider import IdentityProvider
from application.services import UserService
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer()


@inject
async def get_current_user(
    user_service: FromDishka[UserService],
    openid_provider: FromDishka[IdentityProvider],
    token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> Any:
    """
    Retrieve the current user based on a JWT token.

    :param user_service: UserService.
    :param openid_provider: OpenID provider.
    :param token: The authorization token.

    :return: User object.
    """
    logger.debug("Retrieving current user from token.")
    decoded_token = await openid_provider.decode_token(token.credentials)
    user_from_token = CurrentUser.from_token(
        decoded_token,
        decoded_token["azp"],
    )

    return await user_service.get_by_username(user_from_token.username)


@inject
async def get_current_user_from_token(
    openid_provider: FromDishka[IdentityProvider],
    token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> Any:
    """
    Retrieve the current user based on a JWT token.

    :param openid_provider: OpenID provider.
    :param token: The authorization token.

    :return: User object.
    """
    logger.debug("Retrieving current user from token test.")
    decoded_token = await openid_provider.decode_token(token.credentials)

    return CurrentUser.from_token(
        decoded_token,
        decoded_token["azp"],
    )
