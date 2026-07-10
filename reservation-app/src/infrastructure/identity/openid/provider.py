"""Defines the service for working with the OpenID authorization."""

import logging
from typing import Any

import aiohttp
import httpx
from application.ports.providers.identity.provider import IdentityProvider
from core.bootstrap.exceptions import PermissionDeniedError, UnauthorizedError
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials
from infrastructure.identity.openid import UserInfo
from joserfc import jwt
from joserfc.jwk import KeySet

logger = logging.getLogger(__name__)


class OpenIdProvider(IdentityProvider):
    """OpenID client for authentication operations."""

    def __init__(self, client: Any, client_id: str, client_secret: str) -> None:
        self.client = client
        self.client_id = client_id
        self.client_secret = client_secret
        self.jwt = jwt
        self.allowed_algorithms = ["RS256", "ES256", "HS256"]

    async def decode_token(self, token: str) -> dict[str, Any]:
        try:
            metadata = await self.client.load_server_metadata()
            jwks_uri = metadata["jwks_uri"]

            async with aiohttp.ClientSession() as session, session.get(jwks_uri) as resp:
                try:
                    jwks = await resp.json()
                except aiohttp.ContentTypeError as e:
                    text = await resp.text()
                    logger.exception("JWKS endpoint returned non-JSON: %s", text)
                    msg = "Invalid JWKS response"
                    raise UnauthorizedError(msg) from e

            key_set = KeySet.import_key_set(jwks)
            decoded = self.jwt.decode(token, key_set, algorithms=self.allowed_algorithms)
            claims_registry = self.jwt.JWTClaimsRegistry()
            claims_registry.validate(decoded.claims)

            return dict(decoded.claims)

        except aiohttp.ClientError as e:
            logger.info("Token decode failed (network error): %s", e)
            msg = "Unable to fetch JWKS"
            raise UnauthorizedError(msg) from e

        except Exception as e:
            logger.info("Token decode failed: %s", e)
            msg = "Invalid or expired token"
            raise UnauthorizedError(msg) from e

    async def get_user_info(self, token: HTTPAuthorizationCredentials) -> UserInfo:
        token_dict = {"access_token": token.credentials, "token_type": token.scheme}

        try:
            resp = await self.client.userinfo(token=token_dict)
            return UserInfo(**resp)

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code

            if status_code == status.HTTP_401_UNAUTHORIZED:
                logger.info("Invalid or expired token when calling userinfo: %s", e)
                msg = "Invalid or expired token"
                raise UnauthorizedError(message=msg) from e

            if status_code == status.HTTP_403_FORBIDDEN:
                logger.info("Forbidden: token lacks permissions: %s", e)
                msg = "Token lacks required permissions"
                raise PermissionDeniedError(message=msg) from e

            logger.exception("Unexpected HTTP error from userinfo: %s")
            msg = "OIDC provider rejected the request"
            raise UnauthorizedError(message=msg) from e

        except httpx.RequestError as e:
            logger.exception("Network error when contacting OIDC provider: %s")
            msg = "OIDC provider unreachable"
            raise UnauthorizedError(message=msg) from e

        except Exception as e:
            logger.exception("Unexpected error during OIDC userinfo")
            msg = "Failed to retrieve user info"
            raise UnauthorizedError(message=msg) from e

    async def logout(self, refresh_token: str) -> None:
        try:
            metadata = await self.client.load_server_metadata()
            logout_url = metadata.get("end_session_endpoint")
            if not logout_url:
                logger.warning("No end_session_endpoint configured in metadata")
                return

            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    logout_url,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": refresh_token,
                    },
                ) as resp,
            ):
                try:
                    data = await resp.json()
                except aiohttp.ContentTypeError:
                    data = await resp.text()

                logger.info("OIDC logout response (%s): %s", resp.status, data)

                if resp.status == status.HTTP_401_UNAUTHORIZED:
                    msg = "Invalid or missing credentials for logout."
                    raise UnauthorizedError(msg)
                if resp.status == status.HTTP_400_BAD_REQUEST:
                    if isinstance(data, dict):
                        error_desc = data.get("error_description", "Unknown error")
                    else:
                        error_desc = data
                    msg = f"Bad request during logout: {error_desc}"
                    raise UnauthorizedError(msg)
                if resp.status != status.HTTP_204_NO_CONTENT:
                    msg = "Unexpected error during logout"
                    raise PermissionDeniedError(msg)

                logger.info("Logout successful")

        except aiohttp.ClientError as e:
            logger.exception("Network error when contacting OIDC provider: %s")
            msg = "Failed to connect to OIDC provider"
            raise UnauthorizedError(msg) from e
