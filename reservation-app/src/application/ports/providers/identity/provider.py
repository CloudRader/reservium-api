"""Defines an abstract base class for working with the Identity Provider."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from fastapi.security import HTTPAuthorizationCredentials

if TYPE_CHECKING:
    from infrastructure.identity.openid.schemas import UserInfo


class IdentityProvider(ABC):
    """Interface for external authentication providers (SSO)."""

    @abstractmethod
    async def decode_token(self, token: str) -> dict[str, Any]:
        """
        Decode a token.

        This method decodes the given token using provider's public key
        and ensures it is valid. If the token is invalid or expired,
        an HTTP 401 Unauthorized error is raised.

        :param token: The access token to decode.

        :return: A dictionary containing the decoded token information.
        """

    @abstractmethod
    async def get_user_info(self, token: HTTPAuthorizationCredentials) -> UserInfo:
        """
        Get user information from an access token.

        :param token: The access token.

        :return: A dictionary containing user profile information.
        """

    @abstractmethod
    async def logout(self, refresh_token: str) -> None:
        """
        Log out a user by invalidating their refresh token.

        :param refresh_token: The refresh token to invalidate.

        :return: None
        """
