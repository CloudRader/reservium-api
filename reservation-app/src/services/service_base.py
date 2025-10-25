"""
Define an abstract base class AbstractCRUDService.

This class provides a common interface for services that implement CRUD operations on objects.
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from core.application.exceptions import BaseAppError, Entity, EntityNotFoundError
from crud import CRUDBase
from pydantic import BaseModel

SchemaLite = TypeVar("SchemaLite", bound=BaseModel)
SchemaDetail = TypeVar("SchemaDetail", bound=BaseModel)
Crud = TypeVar("Crud", bound=CRUDBase)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class AbstractCRUDService[
    SchemaLite: BaseModel,
    SchemaDetail: BaseModel,
    Crud: CRUDBase,
    CreateSchema: BaseModel,
    UpdateSchema: BaseModel,
](ABC):
    """
    Abstract base class for a CRUD service.

    This class defines a common interface for services that implement CRUD
    (Create, Read, Update, Delete) operations on objects of type `ModelType`.

    Additionally added the read_all implementation.

    By subclassing this class, you can create a CRUD service that works with
    objects of any type `ModelType`.
    """

    @abstractmethod
    async def get(
        self,
        id_: str | int,
        include_removed: bool = False,
    ) -> SchemaDetail:
        """
        Retrieve an object from the database.

        If include_removed is True retrieve a single record
        including marked as deleted.

        :param id_: the ID of the object to retrieve.
        :param include_removed: include removed object or not.

        :returns T: the retrieved object.
        """

    @abstractmethod
    async def get_all(self, include_removed: bool = False) -> list[SchemaLite]:
        """
        Retrieve all objects from the database.

        If include_removed is True retrieve all objects
        including marked as deleted.

        :param include_removed: include removed object or not.

        :returns List[T]: A list of all objects in the database.
        """

    @abstractmethod
    async def create(self, obj_in: CreateSchema) -> SchemaDetail:
        """
        Create an object in the database.

        :param obj_in: the object to create.

        :returns T: the created object.
        """

    @abstractmethod
    async def update(
        self,
        id_: str | int,
        obj_in: UpdateSchema,
    ) -> SchemaDetail:
        """
        Update an object in the database.

        :param id_: the ID of the object to update.
        :param obj_in: the updated object.

        :returns T: the updated object.
        """

    @abstractmethod
    async def restore(self, id_: str | int) -> SchemaDetail:
        """
        Restore a previously soft-removed object by its ID.

        :param id_: The ID of the object to restore.

        :returns T: The restored object.
        """

    @abstractmethod
    async def delete(self, id_: str | int, hard_remove: bool = False) -> SchemaDetail:
        """
        Delete an object from the database.

        :param id_: The ID of the object to delete.
        :param hard_remove: hard remove the object or not.
        """


class CrudServiceBase(
    AbstractCRUDService[SchemaLite, SchemaDetail, Crud, CreateSchema, UpdateSchema]
):
    """
    A base class for implementing a CRUD (Create, Read, Update, Delete).

    Service with methods for creating, reading, reading all, updating and deleting objects.

    It's a generic class that takes three type parameters:

    ModelType which represents the type of objects being stored in the database,
    CreateSchema which represents the input data for creating objects, and
    UpdateSchema which represents the input data for updating objects.
    """

    def __init__(self, crud: Crud, entity_name: Entity):
        self.crud: Crud = crud
        self.entity_name: Entity = entity_name

    async def get(
        self,
        id_: str | int,
        include_removed: bool = False,
    ) -> SchemaDetail:
        obj = await self.crud.get(id_, include_removed)
        if obj is None:
            raise EntityNotFoundError(self.entity_name, id_)
        return obj

    async def get_all(self, include_removed: bool = False) -> list[SchemaLite]:
        return await self.crud.get_all(include_removed)

    async def create(self, obj_in: CreateSchema) -> SchemaDetail:
        return await self.crud.create(obj_in)

    async def update(
        self,
        id_: str | int,
        obj_in: UpdateSchema,
    ) -> SchemaDetail:
        obj_to_update = await self.get(id_)
        if obj_to_update is None:
            raise EntityNotFoundError(self.entity_name, id_)
        return await self.crud.update(db_obj=obj_to_update, obj_in=obj_in)

    async def restore(self, id_: str | int) -> SchemaDetail:
        obj = await self.get(id_, True)
        if obj.deleted_at is None:  # type: ignore
            raise BaseAppError(f"A {self.entity_name.value} was not soft deleted.")
        if obj is None:
            raise EntityNotFoundError(self.entity_name, id_)
        return await self.crud.restore(obj)

    async def delete(self, id_: str | int, hard_remove: bool = False) -> SchemaDetail:
        obj = await self.get(id_, True)
        if hard_remove:
            return await self.crud.remove(id_)
        if obj.deleted_at is not None:  # type: ignore
            raise BaseAppError(f"A {self.entity_name.value} is already soft deleted.")
        return await self.crud.soft_remove(obj)
