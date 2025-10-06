"""Module for authenticator functions."""

from collections.abc import Callable
from typing import Annotated, Any, TypeVar

from api.permissions import PERMISSION_MAP
from core.application.exceptions import Entity
from fastapi import Depends, Path, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from integrations.keycloak import KeycloakAuthService
from integrations.spicedb import SpiceDbService
from services import UserService

http_bearer = HTTPBearer()


TService = TypeVar("TService")
TBody = TypeVar("TBody")


def check_permissions[TService, TBody](
    entity: Entity,
    service_dep: Callable[..., TService],
    action: str,
    body_type: type[TBody] | None = None,
):
    """Dependency that checks if the current user has at least one of the required roles."""

    async def with_id(
        id_: Annotated[str | int, Path(alias="id", description="The ID of the object.")],
        token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
        keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
        spicedb_service: Annotated[SpiceDbService, Depends(SpiceDbService)],
        service: Annotated[TService, Depends(service_dep)],
    ):
        permission = PERMISSION_MAP.get(entity, {}).get(action)
        reservation_service = await service.get_reservation_service(id_)
        token_info = await keycloak_service.decode_token(token.credentials)
        await spicedb_service.check_permissions(
            "area", reservation_service.alias, permission, token_info["preferred_username"]
        )

    async def without_id(
        obj_create: body_type,
        token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
        keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
        spicedb_service: Annotated[SpiceDbService, Depends(SpiceDbService)],
        service: Annotated[TService, Depends(service_dep)],
    ):
        permission = PERMISSION_MAP.get(entity, {}).get(action)
        token_info = await keycloak_service.decode_token(token.credentials)
        if entity == Entity.RESERVATION_SERVICE:
            await spicedb_service.check_permissions(
                "area", obj_create.alias, permission, token_info["preferred_username"]
            )
            return
        reservation_service = await service.get_reservation_service(
            obj_create.reservation_service_id
        )
        token_info = await keycloak_service.decode_token(token.credentials)
        await spicedb_service.check_permissions(
            "area", reservation_service.alias, permission, token_info["preferred_username"]
        )

    async def hard_remove(
        id_: Annotated[str | int, Path(alias="id", description="The ID of the object.")],
        token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
        keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
        spicedb_service: Annotated[SpiceDbService, Depends(SpiceDbService)],
        service: Annotated[TService, Depends(service_dep)],
        hard_remove: bool = Query(False, description="`Hard remove` the object or not."),
    ):
        action_delete = "delete"
        if hard_remove:
            action_delete = "hard_remove"
        permission = PERMISSION_MAP.get(entity, {}).get(action_delete)
        reservation_service = await service.get_reservation_service(id_)
        token_info = await keycloak_service.decode_token(token.credentials)
        await spicedb_service.check_permissions(
            "area", reservation_service.alias, permission, token_info["preferred_username"]
        )

    if action in {"create", "create_multiple"}:
        return without_id
    if action in {"delete"}:
        return hard_remove
    return with_id


async def get_current_user(
    user_service: Annotated[UserService, Depends(UserService)],
    keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
    token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> Any:
    """
    Retrieve the current user based on a JWT token.

    :param user_service: UserLite service.
    :param keycloak_service: IsService service.
    :param token: The authorization token.

    :return: User object.
    """
    user_keycloak = await keycloak_service.get_user_info(token.credentials)
    return await user_service.get(user_keycloak.ldap_id)
