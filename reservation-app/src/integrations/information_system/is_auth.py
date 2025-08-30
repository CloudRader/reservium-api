"""Defines an abstract base class for working with the IS authorization."""

import secrets
from abc import ABC, abstractmethod
from urllib.parse import urlencode

import aiohttp
from core import settings
from core.application.exceptions import UnauthorizedError
from core.schemas.data_is import TokenResponse
from fastapi import status


class AbstractIsAuthService(ABC):
    """Interface for a service interacting with the IS Auth flow."""

    @abstractmethod
    async def generate_is_oauth_redirect_uri(self) -> str:
        """
        Generate the authorization URL for the IS OAuth2 login flow.

        This function constructs the redirect URI with the necessary
        query parameters (client ID, redirect URI, response type, and scope).
        The returned URL should be used to redirect the user to the IS
        authorization server to begin the OAuth2 flow.

        :return: Full authorization URL.
        """

    @abstractmethod
    async def get_token_response(
        self,
        code: str,
    ) -> TokenResponse:
        """
        Exchange an OAuth2 authorization code for an access token.

        Sends a POST request to the OAuth2 token endpoint with the authorization code,
        client credentials, and redirect URI. Returns a parsed `TokenResponse` object.

        :param code: The authorization code received from the OAuth2 server after user login.

        :return: A `TokenResponse` instance.
        """


class IsAuthService(AbstractIsAuthService):
    """Service implementation for interacting with the IS Auth flow."""

    def __init__(self):
        self.client_id = settings.IS.CLIENT_ID
        self.client_secret = settings.IS.CLIENT_SECRET
        self.redirect_uri = settings.IS.REDIRECT_URI
        self.response_type = settings.IS.RESPONSE_TYPE
        self.grant_type = settings.IS.GRANT_TYPE
        self.scope = settings.IS.SCOPE
        self.oauth_url = settings.IS.OAUTH
        self.token_url = settings.IS.OAUTH_TOKEN

    async def generate_is_oauth_redirect_uri(self) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": self.response_type,
            "scope": self.scope,
            "state": secrets.token_urlsafe(16),
        }
        return f"{self.oauth_url}?{urlencode(params)}"

    async def get_token_response(
        self,
        code: str,
    ) -> TokenResponse:
        async with (
            aiohttp.ClientSession() as client,
            client.post(
                self.token_url,
                data={
                    "grant_type": self.grant_type,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            ) as token_response,
        ):
            if token_response.status == status.HTTP_401_UNAUTHORIZED:
                raise UnauthorizedError(
                    "There's some kind of authorization problem",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token_response.raise_for_status()
            response_data = await token_response.json()

        response_data["token_type"] = response_data["token_type"].capitalize()
        return TokenResponse(**response_data)
