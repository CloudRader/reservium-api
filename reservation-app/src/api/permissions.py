"""Utilities for permission checking."""

import logging
from collections.abc import Callable
from typing import Annotated, TypeVar

from api.dependencies import get_current_user_from_token
from core.application.exceptions import BaseAppError, PermissionDeniedError
from core.schemas.keycloak import CurrentUser
from fastapi import Depends, Path
from services import CrudServiceBase, ReservationServiceService

logger = logging.getLogger(__name__)


TService = TypeVar("TService", bound=CrudServiceBase)
TBody = TypeVar("TBody")


def abac_manage_rs_from_body[TService: CrudServiceBase, TBody](
    body_type: type[TBody],
):
    """
    Attribute-Based Access Control (ABAC).

    Dependency that authorizes access based on a reservation service reference contained
    in the request body.

    :param body_type: Pydantic model type representing the request body.

    :return: A FastAPI dependency callable enforcing ABAC rules for body-based access.
    """

    async def dependency(
        user: Annotated[CurrentUser, Depends(get_current_user_from_token)],
        service: Annotated[ReservationServiceService, Depends(ReservationServiceService)],
        obj_create: body_type,
    ):
        reservation_service = await service.get(obj_create.reservation_service_id)

        if not reservation_service:
            raise BaseAppError(message="Missing reservation service")

        if not any(role == f"service_admin:{reservation_service.alias}" for role in user.roles):
            raise PermissionDeniedError(
                message=f"You are not manager of {reservation_service.alias}"
            )

    return dependency


def abac_manage_rs_by_id[TService: CrudServiceBase](
    service_dep: Callable[..., TService],
):
    """

    Attribute-Based Access Control (ABAC).

    Dependency that authorizes access based on a resource identifier provided in the request path.

    :param service_dep: FastAPI dependency provider for the service used to fetch
    reservation service data.

    :return: A FastAPI dependency callable enforcing ABAC rules for ID-based access.
    """

    async def dependency(
        user: Annotated[CurrentUser, Depends(get_current_user_from_token)],
        service: Annotated[TService, Depends(service_dep)],
        id_: Annotated[str | int, Path(alias="id")],
    ):
        reservation_service = await service.get_reservation_service(id_)

        if not reservation_service:
            raise BaseAppError(message="Missing reservation service")

        if not any(role == f"service_admin:{reservation_service.alias}" for role in user.roles):
            raise PermissionDeniedError(
                message=f"You are not manager of {reservation_service.alias}"
            )

    return dependency


def require_permission(*permissions: str):
    """
    FastAPI dependency for enforcing RBAC and optional ABAC authorization.

    :param permissions: One or more RBAC permission strings required to access the endpoint.

    :return: FastAPI dependency function.
    """

    async def dependency(
        user: Annotated[CurrentUser, Depends(get_current_user_from_token)],
    ):
        """
        Execute the FastAPI dependency for permission validation.

        :param user: Current authenticated user.
        """
        if not permissions:
            return

        if not any(user.has_permission(p) for p in permissions):
            raise PermissionDeniedError(message=f"Missing required permission: {permissions}")

    return dependency
