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
        logger.info(
            "ABAC_BODY_CHECK user_id=%s reservation_service_id=%s",
            user.id,
            obj_create.reservation_service_id,
        )

        reservation_service = await service.get(obj_create.reservation_service_id)

        if not reservation_service:
            logger.warning(
                "ABAC_BODY_DENY reason=missing_service user_id=%s "
                "reservation_service_id=%s not_found",
                user.id,
                obj_create.reservation_service_id,
            )
            raise BaseAppError(message="Missing reservation service")

        if not any(role == f"service_admin:{reservation_service.alias}" for role in user.roles):
            logger.warning(
                "ABAC_BODY_DENY reason=missing_role user_id=%s service=%s roles=%s",
                user.id,
                reservation_service.alias,
                user.roles,
            )
            raise PermissionDeniedError(
                message=f"You are not manager of {reservation_service.alias}"
            )

        logger.info(
            "ABAC_BODY_ALLOW user_id=%s service=%s",
            user.id,
            reservation_service.alias,
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
        logger.info(
            "ABAC_ID_CHECK user_id=%s id=%s",
            user.id,
            id_,
        )

        reservation_service = await service.get_reservation_service(id_)

        if not reservation_service:
            logger.warning(
                "ABAC_ID_DENY reason=missing_service user_id=%s",
                user.id,
            )
            raise BaseAppError(message="Missing reservation service")

        if not any(role == f"service_admin:{reservation_service.alias}" for role in user.roles):
            logger.warning(
                "ABAC_ID_DENY reason=missing_role user_id=%s service=%s roles=%s",
                user.id,
                reservation_service.alias,
                user.roles,
            )
            raise PermissionDeniedError(
                message=f"You are not manager of {reservation_service.alias}"
            )

        logger.info(
            "ABAC_ID_ALLOW user_id=%s service=%s",
            user.id,
            reservation_service.alias,
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
        logger.info(
            "RBAC_CHECK user_id=%s permissions=%s",
            user.id,
            permissions,
        )

        if not permissions:
            return

        if not any(user.has_permission(p) for p in permissions):
            logger.warning(
                "RBAC_DENY user_id=%s required=%s user_permissions=%s",
                user.id,
                permissions,
                user.roles,
            )
            raise PermissionDeniedError(message=f"Missing required permission: {permissions}")

        logger.info("RBAC_ALLOW user_id=%s", user.id)

    return dependency
