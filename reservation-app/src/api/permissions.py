"""Utilities for permission checking."""

import logging
from collections.abc import Callable
from typing import Annotated, TypeVar

from api.dependencies import get_current_user_from_token
from core.application.exceptions import BaseAppError, PermissionDeniedError
from core.schemas.keycloak import CurrentUser
from fastapi import Depends, Path
from services import CrudServiceBase

logger = logging.getLogger(__name__)


TService = TypeVar("TService", bound=CrudServiceBase)
TBody = TypeVar("TBody")


async def handle_abac(
    rule: str,
    user: CurrentUser,
    service: CrudServiceBase,
    id_: str | int | None,
):
    """
    Execute Attribute-Based Access Control (ABAC) checks for a given rule.

    :param rule: Name of the ABAC rule to apply.
    :param user: The currently authenticated user.
    :param service: Service instance used to fetch domain objects.
    :param id_: Identifier of the target resource (if applicable).
    """
    if rule == "manage_reservation_service":
        reservation_service = await service.get_reservation_service(id_)

        if not reservation_service:
            raise BaseAppError(message="Missing reservation service")

        if not any(role == f"service_admin:{reservation_service.alias}" for role in user.roles):
            raise PermissionDeniedError(
                message=f"You are not manager of {reservation_service.alias}"
            )


def require_permission[TService: CrudServiceBase](
    *permissions: str,
    abac: str | None = None,
    service_dep: Callable[..., TService],
):
    """
    FastAPI dependency for enforcing RBAC and optional ABAC authorization.

    :param permissions: One or more RBAC permission strings required to access the endpoint.
    :param abac: Optional ABAC rule name for resource-level authorization.
    :param service_dep: Callable that returns the service instance to use for domain logic.

    :return: FastAPI dependency function.
    """

    async def dependency(
        user: Annotated[CurrentUser, Depends(get_current_user_from_token)],
        service: Annotated[TService, Depends(service_dep)],
        id_: Annotated[str | int, Path(alias="id")],
    ):
        """
        Execute the FastAPI dependency for permission validation.

        :param user: Current authenticated user.
        :param service: Injected service for accessing domain logic.
        :param id_: Resource identifier from request path.
        """
        # --- RBAC ---
        if not any(user.has_permission(p) for p in permissions):
            raise PermissionDeniedError(message=f"Missing required permission: {permissions}")

        # --- ABAC ---
        if abac:
            await handle_abac(abac, user, service, id_)

    return dependency
