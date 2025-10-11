"""Defines the service for working with the Keycloak authorization."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from core import settings
from core.application.exceptions import PermissionDeniedError, UnauthorizedError
from core.schemas import UserKeycloak
from jwcrypto.common import JWException
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError, KeycloakGetError

logger = logging.getLogger(__name__)


class AbstractKeycloakAuthService(ABC):
    """Interface for a service interacting with the Keycloak Auth flow."""

    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> dict[str, Any]:
        """
        Authenticate a user with Keycloak.

        :param username: The username of the user.
        :param password: The password of the user.

        :return: A dictionary containing the token response from Keycloak.
        """

    @abstractmethod
    async def validate_token(self, token: str) -> dict[str, Any]:
        """
        Validate an access token with Keycloak.

        :param token: The access token to validate.

        :return: A dictionary with decoded token or user information if valid.
        """

    @abstractmethod
    async def decode_token(self, token: str) -> dict[str, Any]:
        """
        Decode a Keycloak token.

        This method decodes the given token using Keycloak's public key
        and ensures it is valid. If the token is invalid or expired,
        an HTTP 401 Unauthorized error is raised.

        :param token: The access token to decode.

        :return: A dictionary containing the decoded token information.
        :raises JWException: If the token is invalid or expired.
        """

    @abstractmethod
    async def get_user_info(self, token: str) -> dict[str, Any]:
        """
        Get user information from an access token.

        :param token: The access token.

        :return: A dictionary containing user profile information.
        """

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Refresh an access token using a refresh token.

        :param refresh_token: The refresh token.

        :return: A dictionary containing the refreshed token response.
        """

    @abstractmethod
    async def logout(self, refresh_token: str) -> None:
        """
        Log out a user by invalidating their refresh token.

        :param refresh_token: The refresh token to invalidate.

        :return: None
        """


class KeycloakAuthService(AbstractKeycloakAuthService):
    """Keycloak client for authentication operations."""

    def __init__(self):
        self.keycloak_openid = KeycloakOpenID(
            server_url=settings.KEYCLOAK.SERVER_URL,
            client_id=settings.KEYCLOAK.CLIENT_ID,
            realm_name=settings.KEYCLOAK.REALM,
            client_secret_key=settings.KEYCLOAK.CLIENT_SECRET,
        )

    async def authenticate_user(self, username: str, password: str) -> dict[str, Any]:
        try:
            return self.keycloak_openid.token(username, password)
        except KeycloakAuthenticationError as e:
            logger.info("Keycloak authentication failed: %s", e)
            raise UnauthorizedError(
                message="Invalid username or password",
            ) from e

    async def validate_token(self, token: str) -> dict[str, Any]:
        try:
            # Validate token and get user info
            return self.keycloak_openid.userinfo(token)
        except KeycloakAuthenticationError as e:
            logger.info("Token validation failed: %s", e)
            raise UnauthorizedError(
                message="Invalid or expired token",
            ) from e

    async def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return self.keycloak_openid.decode_token(token)
        except JWException as e:
            logger.info("Token validation failed: %s", e)
            raise UnauthorizedError(
                message="Invalid or expired token",
            ) from e

    async def get_user_info(self, token: str) -> UserKeycloak:
        try:
            user_info = UserKeycloak(**(self.keycloak_openid.userinfo(token)))
            logger.debug("Retrieved user info from Keycloak for sub=%s", user_info.sub)
            return user_info
        except KeycloakAuthenticationError as e:
            logger.info("Failed to get user info: %s", e)
            raise UnauthorizedError(
                message="Failed to retrieve user information",
            ) from e
        except KeycloakGetError as e:
            logger.info("Insufficient token permissions: %s", e)
            raise PermissionDeniedError(
                message="Token lacks required permissions",
            ) from e

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        try:
            return self.keycloak_openid.refresh_token(refresh_token)
        except KeycloakAuthenticationError as e:
            logger.info("Token refresh failed: %s", e)
            raise UnauthorizedError(
                message="Invalid or expired refresh token",
            ) from e

    async def logout(self, refresh_token: str) -> None:
        try:
            self.keycloak_openid.logout(refresh_token)
        except KeycloakAuthenticationError as e:
            logger.info("Logout failed: %s", e)
            # Don't raise exception for logout failures
