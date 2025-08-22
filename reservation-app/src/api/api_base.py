"""Base module for generating CRUD routes in FastAPI."""

from collections.abc import Callable
from typing import Annotated, Any, TypeVar

from api.user_authenticator import get_current_user
from core.application.exceptions import ERROR_RESPONSES, BaseAppError, Entity, EntityNotFoundError
from core.schemas.user import UserLite
from fastapi import APIRouter, Depends, Path, Query, status
from pydantic import BaseModel
from services.service_base import CrudServiceBase

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
            include_removed: bool = Query(False),
        ):
            """
            Get all objects from database.

            :param service: Service providing business logic of this object.
            :param include_removed: include removed object or not.

            :return: List of all objects or None if there are no objects in db.
            """
            return await service.get_all(include_removed)

    def register_get_by_id(self):
        """Register the GET /{obj_id} endpoint to retrieve an entity by its ID."""
        schema_detail: type[TReadDetail] = self.schema_detail
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.get(
            "/{obj_id}",
            response_model=schema_detail,
            responses=ERROR_RESPONSES["404"],
            status_code=status.HTTP_200_OK,
        )
        async def get_by_id(
            service: Annotated[service_dep, Depends(service_dep)],
            obj_id: Annotated[str | int, Path()],
            include_removed: bool = Query(False),
        ):
            """
            Get object by its uuid.

            :param service: Service providing business logic of this object.
            :param obj_id: uuid of the object.
            :param include_removed: include removed object or not.

            :return: Object with id equal to id
                     or None if no such object exists.
            """
            obj = await service.get(obj_id, include_removed)
            return await self._handle_not_found(obj, obj_id)

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
            """
            Create object, only users with special roles can create object.

            :param service: Service providing business logic of this object.
            :param user: UserLite who make this request.
            :param obj_create: ObjectCreate schema.

            :returns ObjectSchema: the created object.
            """
            return await self._create_single_object(service, user, obj_create)

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
            """
            Create objects, only users with special roles can create object.

            :param service: Service providing business logic of this object.
            :param user: UserLite who make this request.
            :param objs_create: ObjectsCreate schema.

            :returns list created ObjectSchema: the created objects.
            """
            objs_result: list[schema_detail] = []
            for obj_create in objs_create:
                objs_result.append(await self._create_single_object(service, user, obj_create))
            return objs_result

    def register_update(self):
        """Register the PUT /{obj_id} endpoint to update an existing entity."""
        schema_update: type[TUpdate] = self.schema_update
        schema_detail: type[TReadDetail] = self.schema_detail
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.put(
            "/{obj_id}",
            response_model=schema_detail,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def update(
            service: Annotated[service_dep, Depends(service_dep)],
            user: Annotated[UserLite, Depends(get_current_user)],
            obj_id: Annotated[str | int, Path()],
            obj_update: schema_update,
        ):
            """
            Update object with uuid equal to 'obj_id'.

            Only users with special roles can update object.

            :param service: Service providing business logic of this object.
            :param user: UserLite who make this request.
            :param obj_id: id of the object.
            :param obj_update: ObjectUpdate schema.

            :returns ObjectSchema: the updated object.
            """
            obj = await service.update_with_permission_checks(obj_id, obj_update, user)
            return await self._handle_not_found(obj, obj_id)

    def register_restore(self):
        """Register the PUT /{obj_id}/restore endpoint to restore soft delete entity."""
        schema_detail: type[TReadDetail] = self.schema_detail
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.put(
            "/{obj_id}/restore",
            response_model=schema_detail,
            responses=ERROR_RESPONSES["400_401_403"],
            status_code=status.HTTP_200_OK,
        )
        async def restore(
            service: Annotated[service_dep, Depends(service_dep)],
            user: Annotated[UserLite, Depends(get_current_user)],
            obj_id: Annotated[str | int, Path()],
        ):
            """
            Retrieve deleted object with id equal to 'obj_id'.

            Only users with special roles can update object.

            :param service: Service providing business logic of this object.
            :param user: UserLite who make this request.
            :param obj_id: id of the object.

            :returns ObjectSchema: the restored object.
            """
            obj = await service.restore_with_permission_checks(obj_id, user)
            return await self._handle_not_found(obj, obj_id)

    def register_delete(self):
        """Register the DELETE /{obj_id} endpoint to delete an entity."""
        schema_lite: type[TReadLite] = self.schema_lite
        service_dep: Callable[..., TService] = self.service_dep

        @self.router.delete(
            "/{obj_id}",
            response_model=schema_lite,
            responses=ERROR_RESPONSES["400_401_403_404"],
            status_code=status.HTTP_200_OK,
        )
        async def delete(
            service: Annotated[service_dep, Depends(service_dep)],
            user: Annotated[UserLite, Depends(get_current_user)],
            obj_id: Annotated[str | int, Path()],
            hard_remove: bool = Query(False),
        ):
            """
            Delete object with obj_id equal to 'id'.

            Only users with special roles can delete object.

            :param service: Service providing business logic of this object.
            :param user: UserLite who make this request.
            :param obj_id: id of the object.
            :param hard_remove: hard remove of the object or not.

            :returns ObjectSchema: the deleted object.
            """
            obj = await service.delete_with_permission_checks(obj_id, user, hard_remove)
            return await self._handle_not_found(obj, obj_id)

    # ---------- helpers ----------
    async def _handle_not_found(self, obj: TReadDetail, identifier: Any) -> TReadDetail:
        """Raise EntityNotFoundError if obj falsy, otherwise return it."""
        if not obj:
            raise EntityNotFoundError(self.entity_name, identifier)
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
