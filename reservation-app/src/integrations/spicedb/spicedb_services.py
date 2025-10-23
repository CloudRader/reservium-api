"""Defines the service for working with the SpiceDB authorization."""

import logging
from abc import ABC, abstractmethod

import aiohttp
from core import settings
from core.application.exceptions import (
    BaseAppError,
    ExternalAPIError,
    PermissionDeniedError,
    UnauthorizedError,
)
from fastapi import status

logger = logging.getLogger(__name__)


class AbstractSpiceDbService(ABC):
    """Interface for a service interacting with the SpiceDB Auth flow."""

    @abstractmethod
    async def check_permissions(
        self,
        resource_type: str,
        resource_id: str,
        permission: str,
        subject: str,
    ) -> bool:
        """
        Check whether the given subject has a specific permission on a resource.

        :param resource_type: The type of the resource to check access against.
        :param resource_id: The identifier of the resource to check access against.
        :param permission: The name of the permission to verify (e.g., "read", "write").
        :param subject: The identifier of the subject (e.g., a user or role) requesting access.

        :return bool: True if the subject has the requested permission on the resource.
        """


class SpiceDbService(AbstractSpiceDbService):
    """SpiceDb client for authentication operations."""

    def __init__(self):
        self.server_url = settings.SPICEDB.SERVER_URL
        self.secret = settings.SPICEDB.CLIENT_SECRET

    async def check_permissions(
        self,
        resource_type: str,
        resource_id: str,
        permission: str,
        subject: str,
    ) -> bool:
        url = f"{self.server_url}/v1/permissions/check"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.secret}",
        }
        payload = {
            "resource": {
                "objectType": resource_type,
                "objectId": resource_id,
            },
            "permission": permission,
            "subject": {
                "object": {
                    "objectType": "user",
                    "objectId": subject,
                }
            },
        }

        logger.info("Sending SpiceDB check request: %s", payload)

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(url, headers=headers, json=payload) as resp,
            ):
                data = await resp.json()
                logger.info("SpiceDB response (%s): %s", resp.status, data)

                if resp.status == status.HTTP_401_UNAUTHORIZED:
                    raise UnauthorizedError(message="Invalid or missing SpiceDB credentials.")

                if resp.status == status.HTTP_400_BAD_REQUEST:
                    raise BaseAppError(message=data["message"])

                if resp.status != 200:
                    raise ExternalAPIError(message="SpiceDB error")

                if data.get("permissionship") != "PERMISSIONSHIP_HAS_PERMISSION":
                    raise PermissionDeniedError(
                        f"Subject {subject} has no '{permission}' permission "
                        f"on resource {resource_id}."
                    )

                return True

        except aiohttp.ClientError as e:
            logger.exception("Failed to reach SpiceDB: %s", e)
            raise ExternalAPIError("Failed to connect to SpiceDB.") from e
