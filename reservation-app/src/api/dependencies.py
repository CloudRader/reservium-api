"""Module for authenticator functions."""

import logging
from typing import Annotated, Any

from api.schemas.current_user import CurrentUser
from application.ports.providers.identity.provider import IdentityProvider
from application.services import (
    CalendarService,
    EventService,
    MiniServiceService,
    ReservationServiceService,
    UserService,
)
from core.bootstrap.container import Container
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from infrastructure.database import AsyncSessionDep

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer()


async def get_container(db: AsyncSessionDep) -> Container:
    """Retrieve Session instance using DI container."""
    return Container(db)


async def get_identity_provider(
    container: Annotated[Container, Depends(get_container)],
) -> IdentityProvider:
    """Retrieve IdentityProvider instance using DI container."""
    return container.identity_provider()


async def get_user_service(
    container: Annotated[Container, Depends(get_container)],
) -> UserService:
    """Retrieve UserService instance using DI container."""
    return container.user_service()


async def get_calendar_service(
    container: Annotated[Container, Depends(get_container)],
) -> CalendarService:
    """Retrieve CalendarService instance using DI container."""
    return container.calendar_service()


async def get_event_service(
    container: Annotated[Container, Depends(get_container)],
) -> EventService:
    """Retrieve EventService instance using DI container."""
    return container.event_service()


async def get_mini_service_service(
    container: Annotated[Container, Depends(get_container)],
) -> MiniServiceService:
    """Retrieve MiniServiceService instance using DI container."""
    return container.mini_service_service()


async def get_reservation_service_service(
    container: Annotated[Container, Depends(get_container)],
) -> ReservationServiceService:
    """Retrieve ReservationServiceService instance using DI container."""
    return container.reservation_service_service()


async def get_current_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    openid_service: Annotated[IdentityProvider, Depends(get_identity_provider)],
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
    openid_service: Annotated[IdentityProvider, Depends(get_identity_provider)],
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
