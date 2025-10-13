"""Utilities for permission checking."""

import logging
from collections.abc import Callable
from typing import Annotated, TypeVar

from core import settings
from core.application.exceptions import BaseAppError, Entity, PermissionDeniedError
from fastapi import Depends, Path, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from integrations.keycloak import KeycloakAuthService
from services import CrudServiceBase

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer()

PERMISSION_MAP = {
    Entity.RESERVATION_SERVICE: {
        "create": "admin",
        "create_multiple": "admin",
        "update": "admin",
        "restore": "admin",
        "delete": "admin",
        "hard_remove": "admin",
    },
    Entity.CALENDAR: {
        "create": "manage",
        "create_multiple": "admin",
        "update": "manage",
        "restore": "manage",
        "delete": "manage",
        "hard_remove": "admin",
    },
    Entity.MINI_SERVICE: {
        "create": "manage",
        "create_multiple": "admin",
        "update": "manage",
        "restore": "manage",
        "delete": "manage",
        "hard_remove": "admin",
    },
}


TService = TypeVar("TService", bound=CrudServiceBase)
TBody = TypeVar("TBody")


async def check_admin_permission(
    permission: str,
    token_info: dict,
) -> bool:
    """Verify that the current user has the admin role."""
    if permission == "admin":
        roles = token_info["resource_access"][settings.KEYCLOAK.CLIENT_ID]["roles"]
        if permission not in roles:
            raise PermissionDeniedError(message="You must be an admin to do this operation.")
        return True
    return False


async def check_manager_permission(
    roles: list[str],
    alias: str,
) -> bool:
    """Verify that the current user is a manager for a given alias."""
    for role in roles:
        if role.startswith("service_admin:"):
            service_name = role.split(":", 1)[1]
            if service_name == alias:
                return True

    raise PermissionDeniedError(message=f"You must be the {alias} manager to do this operation.")


def check_create_permissions[TService, TBody](
    service_dep: Callable[..., TService],
    body_type: type[TBody],
):
    """Dependency for create actions."""

    async def dependency(
        obj_create: body_type,
        token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
        keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
        service: Annotated[TService, Depends(service_dep)],
    ):
        entity = getattr(service, "entity_name", None)
        token_info = await keycloak_service.decode_token(token.credentials)
        entity_value = getattr(entity, "value", None)

        logger.info(
            "User %s creating %s: %s", token_info["preferred_username"], entity_value, obj_create
        )

        permission = PERMISSION_MAP.get(entity, {}).get("create") or ""

        if await check_admin_permission(permission, token_info):
            return

        if permission == "manage":
            reservation_service_id = getattr(obj_create, "reservation_service_id", None)
            if not reservation_service_id:
                logging.warning("Reservation service id is missing in %s", obj_create)
                raise BaseAppError(message="Unexpected permission problem, contact administrator.")

            if not getattr(service, "reservation_service_service", None):
                logging.warning(
                    "This object not have a reservation service service. Object %s", obj_create
                )
                raise BaseAppError(message="Unexpected permission problem, contact administrator.")

            reservation_service = await service.reservation_service_service.get(
                reservation_service_id
            )
            if await check_manager_permission(token_info["roles"], reservation_service.alias):
                return

        logging.warning("Unexpected permission provided: %s", permission)
        raise BaseAppError(message="Unexpected permission problem, contact administrator.")

    return dependency


def check_create_multiple_permissions[TService, TBody](
    service_dep: Callable[..., TService],
):
    """Dependency for create actions."""

    async def dependency(
        token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
        keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
        service: Annotated[TService, Depends(service_dep)],
    ):
        entity = getattr(service, "entity_name", None)
        token_info = await keycloak_service.decode_token(token.credentials)
        entity_value = getattr(entity, "value", None)

        logger.info("User %s creating multiple %s", token_info["preferred_username"], entity_value)

        permission = PERMISSION_MAP.get(entity, {}).get("create_multiple") or ""

        if await check_admin_permission(permission, token_info):
            return

        raise BaseAppError(message="Unexpected permission problem, contact administrator.")

    return dependency


def check_update_permissions[TService](
    service_dep: Callable[..., TService],
    action: str,
):
    """Dependency for update actions."""

    async def dependency(
        id_: Annotated[str | int, Path(alias="id")],
        token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
        keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
        service: Annotated[TService, Depends(service_dep)],
    ):
        entity = getattr(service, "entity_name", None)
        token_info = await keycloak_service.decode_token(token.credentials)
        entity_value = getattr(entity, "value", None)

        if action == "update":
            logger.info(
                "User %s updating %s id=%s",
                token_info["preferred_username"],
                entity_value,
                id_,
            )
        else:
            logger.info(
                "User %s restoring %s id=%s", token_info["preferred_username"], entity_value, id_
            )
        permission = PERMISSION_MAP.get(entity, {}).get(action) or ""
        reservation_service = await service.get_reservation_service(id_)

        if await check_admin_permission(permission, token_info):
            return
        if await check_manager_permission(token_info["roles"], reservation_service.alias):
            return

    return dependency


def check_delete_permissions[TService](
    service_dep: Callable[..., TService],
):
    """Dependency for delete actions."""

    async def dependency(
        id_: Annotated[str | int, Path(alias="id")],
        token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
        keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
        service: Annotated[TService, Depends(service_dep)],
        hard_remove: bool = Query(False, description="`Hard remove` the object or not."),
    ):
        entity = getattr(service, "entity_name", None)
        if hard_remove:
            permission = PERMISSION_MAP.get(entity, {}).get("hard_remove") or ""
        else:
            permission = PERMISSION_MAP.get(entity, {}).get("delete") or ""
        reservation_service = await service.get_reservation_service(id_)
        token_info = await keycloak_service.decode_token(token.credentials)

        if await check_admin_permission(permission, token_info):
            return
        if await check_manager_permission(token_info["roles"], reservation_service.alias):
            return
        raise PermissionDeniedError()

    return dependency
