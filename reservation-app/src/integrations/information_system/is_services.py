"""Defines an abstract base class for working with the IS API."""

from abc import ABC, abstractmethod
from typing import Any

import aiohttp
from core import settings
from core.application.exceptions import UnauthorizedError
from core.schemas import Role, RoleList, Room, ServiceList, ServiceValidity, UserIS
from fastapi import status


class AbstractIsService(ABC):
    """Interface for a service interacting with the IS API."""

    @abstractmethod
    async def get_user_data(self, token: str) -> UserIS:
        """
        Get user data from the IS.

        :param token: The authorization token.

        :return: A `UserIS` instance.
        """

    @abstractmethod
    async def get_roles_data(self, token: str) -> RoleList:
        """
        Get roles data from the IS.

        :param token: The authorization token.

        :return: A `UserIS` instance.
        """

    @abstractmethod
    async def get_services_data(self, token: str) -> ServiceList:
        """
        Get services data from the IS.

        :param token: The authorization token.

        :return: A `UserIS` instance.
        """

    @abstractmethod
    async def get_room_data(self, token: str) -> Room:
        """
        Get room data from the IS.

        :param token: The authorization token.

        :return: A `UserIS` instance.
        """


class IsService(AbstractIsService):
    """Service implementation for interacting with the IS API."""

    def __init__(self):
        self.base_url = settings.IS.BASE_URL
        self.user_api_url = "/users/me"
        self.roles_api_url = "/user_roles/mine"
        self.services_api_url = "/services/mine"
        self.room_api_url = "/rooms/mine"

    async def get_user_data(self, token: str) -> UserIS:
        return UserIS(**(await self._get_request(token, self.user_api_url)))

    async def get_roles_data(self, token: str) -> list[Role]:
        return RoleList(roles=await self._get_request(token, self.roles_api_url)).roles

    async def get_services_data(self, token: str) -> list[ServiceValidity]:
        return ServiceList(services=await self._get_request(token, self.services_api_url)).services

    async def get_room_data(self, token: str) -> Room:
        return Room(**(await self._get_request(token, self.room_api_url)))

    async def _get_request(self, token: str, endpoint: str) -> Any:
        """
        Perform an authorized GET request to the IS API.

        :param token: The authorization token.
        :param endpoint: The relative API endpoint (e.g. "/users/me").

        :return: The parsed JSON response. This may be a dictionary or a list,
        depending on the endpoint response format.
        """
        headers = {"Authorization": f"Bearer {token}"}
        full_endpoint = f"{self.base_url}{endpoint}"

        async with (
            aiohttp.ClientSession() as client,
            await client.get(
                full_endpoint,
                headers=headers,
            ) as response,
        ):
            if response.status == status.HTTP_401_UNAUTHORIZED:
                raise UnauthorizedError(
                    "There's some kind of authorization problem",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            response.raise_for_status()
            return await response.json()
