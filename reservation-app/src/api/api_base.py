"""Base module for generating CRUD routes in FastAPI."""

import logging
from collections.abc import Callable
from typing import Annotated, TypeVar

from api import get_current_user
from core.application.exceptions import ERROR_RESPONSES, BaseAppError, Entity
from core.schemas.user import UserLite
from fastapi import APIRouter, Depends, Path, Query, status
from pydantic import BaseModel
from services.service_base import CrudServiceBase

logger = logging.getLogger(__name__)

TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)
TReadLite = TypeVar("TReadLite", bound=BaseModel)
TReadDetail = TypeVar("TReadDetail", bound=BaseModel)
TService = TypeVar("TService", bound=CrudServiceBase)


class BaseCRUDRouter[
    TCreate: BaseModel,
    TUpdate: BaseModel,
    TReadLite: BaseModel,
    TReadDetail: BaseModel,
    TService: CrudServiceBase,
]:
    """
    A base class for automatically registering standard CRUD routes to a FastAPI router.

    This router builder registers endpoints for:
    - GET all
    - GET by ID
    - POST (create)
    - PUT (update)
    - DELETE

    You can selectively disable/enable each operation using the corresponding flags.

    :param router: FastAPI APIRouter instance.
    :param service_dep: Dependency-injected service providing business logic.
    :param schema_create: Pydantic schema used for creating the resource.
    :param schema_update: Pydantic schema used for updating the resource.
    :param schema_lite: Pydantic schema lite used for reading the resource.
    :param schema_detail: Pydantic schema detail used for reading the resource.
    :param entity_name: A human-readable name for the entity (used in error messages).
    :param enable_create: Whether to register the create endpoint.
    :param enable_read: Whether to register the read (get) endpoints.
    :param enable_update: Whether to register the update endpoint.
    :param enable_delete: Whether to register the delete endpoint.
    """

    def __init__(
        self,
        router: APIRouter,
        *,
        service_dep: Callable[..., TService],
        schema_create: type[TCreate],
        schema_update: type[TUpdate],
        schema_lite: type[TReadLite],
        schema_detail: type[TReadDetail],
        entity_name: Entity,
        enable_create: bool = True,
        enable_read: bool = True,
        enable_create_multiple: bool = True,
        enable_update: bool = True,
        enable_restore: bool = True,
        enable_delete: bool = True,
    ):
        self.router = router
        self.service_dep = service_dep
        self.schema_create = schema_create
        self.schema_update = schema_update
        self.schema_lite = schema_lite
        self.schema_detail = schema_detail
        self.entity_name = entity_name

        # route toggles
        self.enable_create = enable_create
        self.enable_create_multiple = enable_create_multiple
        self.enable_read = enable_read
        self.enable_update = enable_update
        self.enable_restore = enable_restore
        self.enable_delete = enable_delete

        self._ROUTES = [
            ("enable_read", self.register_get_all),
            ("enable_read", self.register_get_by_id),
            ("enable_create", self.register_create),
            ("enable_create_multiple", self.register_create_multiple),
            ("enable_update", self.register_update),
            ("enable_restore", self.register_restore),
            ("enable_delete", self.register_delete),
        ]

    # ---------- registration ----------
    def register_routes(self) -> None:
        """Register all enabled routes according to builder flags."""
        for flag, register_fn in self._ROUTES:
            if getattr(self, flag, False):
                register_fn()

    # ---------- route registrations ----------
    def register_get_all(self):
        """Register the GET / endpoint to retrieve all entities."""
        schema_lite: type[TReadLite] = self.schema_lite
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.get(
            "/",
            response_model=list[schema_lite],
            status_code=status.HTTP_200_OK,
        )
        async def get_all(
            service: Annotated[service_dep, Depends(service_dep)],
            include_removed: bool = Query(False, description="Include `removed objects` or not."),
        ):
            """Get all objects."""
            logger.info(
                "Fetching all %s (include_removed=%s)", self.entity_name.value, include_removed
            )
            result = await service.get_all(include_removed)
            logger.debug("Fetched %d objects", len(result))
            return result

    def register_get_by_id(self):
        """Register the GET /{id} endpoint to retrieve an entity by its ID."""
        schema_detail: type[TReadDetail] = self.schema_detail
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.get(
            "/{id}",
            response_model=schema_detail,
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_by_id(
            service: Annotated[service_dep, Depends(service_dep)],
            id_: Annotated[str | int, Path(alias="id", description="The ID of the object.")],
            include_removed: bool = Query(False, description="Include `removed object` or not."),
        ):
            """Get object."""
            logger.info(
                "Fetching %s by id=%s (include_removed=%s)",
                self.entity_name.value,
                id_,
                include_removed,
            )
            obj = await service.get(id_, include_removed)
            logger.debug("Fetched %s: %s", self.entity_name.value, obj)
            return obj

    def register_create(self):
        """Register the POST / endpoint to create a new entity."""
        schema_create: type[TCreate] = self.schema_create
        schema_detail: type[TReadDetail] = self.schema_detail
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.post(
            "/",
            response_model=schema_detail,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_201_CREATED,
        )
        async def create(
            service: Annotated[service_dep, Depends(service_dep)],
            user: Annotated[UserLite, Depends(get_current_user)],
            obj_create: schema_create,
        ):
            """Create object, only users with special roles can create object."""
            logger.info("User %s creating %s: %s", user.id, self.entity_name.value, obj_create)
            obj = await self._create_single_object(service, user, obj_create)
            logger.debug("Created %s: %s", self.entity_name.value, obj)
            return obj

    def register_create_multiple(self):
        """Register the POST / endpoint to create multiple entities."""
        schema_create: type[TCreate] = self.schema_create
        schema_detail: type[TReadDetail] = self.schema_detail
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.post(
            "/batch",
            response_model=list[schema_detail],
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_201_CREATED,
        )
        async def create_multiple(
            service: Annotated[service_dep, Depends(service_dep)],
            user: Annotated[UserLite, Depends(get_current_user)],
            objs_create: list[schema_create],
        ):
            """Create multiple objects in a single request."""
            logger.info(
                "User %s creating multiple %s: count=%d",
                user.id,
                self.entity_name.value,
                len(objs_create),
            )
            objs_result: list[schema_detail] = []
            for obj_create in objs_create:
                obj = await self._create_single_object(service, user, obj_create)
                logger.debug("Created %s: %s", self.entity_name.value, obj)
                objs_result.append(obj)
            return objs_result

    def register_update(self):
        """Register the PUT /{id} endpoint to update an existing entity."""
        schema_update: type[TUpdate] = self.schema_update
        schema_detail: type[TReadDetail] = self.schema_detail
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.put(
            "/{id}",
            response_model=schema_detail,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def update(
            service: Annotated[service_dep, Depends(service_dep)],
            user: Annotated[UserLite, Depends(get_current_user)],
            id_: Annotated[str | int, Path(alias="id", description="The ID of the object.")],
            obj_update: schema_update,
        ):
            """Update object, only users with special roles can update object."""
            logger.info(
                "User %s updating %s id=%s with data: %s",
                user.id,
                self.entity_name.value,
                id_,
                obj_update,
            )
            obj = await service.update_with_permission_checks(id_, obj_update, user)
            logger.debug("Updated %s: %s", self.entity_name.value, obj)
            return obj

    def register_restore(self):
        """Register the PUT /{id}/restore endpoint to restore soft delete entity."""
        schema_detail: type[TReadDetail] = self.schema_detail
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.put(
            "/{id}/restore",
            response_model=schema_detail,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def restore(
            service: Annotated[service_dep, Depends(service_dep)],
            user: Annotated[UserLite, Depends(get_current_user)],
            id_: Annotated[str | int, Path(alias="id", description="The ID of the object.")],
        ):
            """Restore a soft-deleted object, only users with special roles can restore object."""
            logger.info("User %s restoring %s id=%s", user.id, self.entity_name.value, id_)
            obj = await service.restore_with_permission_checks(id_, user)
            logger.debug("Restored object: %s", obj)
            return obj

    def register_delete(self):
        """Register the DELETE /{id} endpoint to delete an entity."""
        schema_lite: type[TReadLite] = self.schema_lite
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.delete(
            "/{id}",
            response_model=schema_lite,
            responses=ERROR_RESPONSES["400_401_403_404"],
            status_code=status.HTTP_200_OK,
        )
        async def delete(
            service: Annotated[service_dep, Depends(service_dep)],
            user: Annotated[UserLite, Depends(get_current_user)],
            id_: Annotated[str | int, Path(alias="id", description="The ID of the object.")],
            hard_remove: bool = Query(False, description="`Hard remove` the object or not."),
        ):
            """Delete object, only users with special roles can delete object."""
            logger.info(
                "User %s deleting %s id=%s (hard_remove=%s)",
                user.id,
                self.entity_name.value,
                id_,
                hard_remove,
            )
            obj = await service.delete_with_permission_checks(id_, user, hard_remove)
            logger.debug("Deleted object: %s", obj)
            return obj

    @staticmethod
    async def _create_single_object(
        service: TService,
        user: UserLite,
        obj_create: TCreate,
    ) -> TReadDetail:
        """
        Help creating a single object with permission checks.

        :param service: Service providing business logic of this object.
        :param user: Authenticated user performing the creation.
        :param obj_create: Data required to create the object.

        :return: The created Object instance.
        """
        obj = await service.create_with_permission_checks(obj_create, user)
        if not obj:
            raise BaseAppError()
        return obj
