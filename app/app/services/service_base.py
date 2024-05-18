"""
This module defines an abstract base class AbstractCRUDService with a common interface
for services that implement CRUD operations on objects
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Row

from db import Base
from crud import CRUDBase

Model = TypeVar("Model", bound=Base)
Crud = TypeVar("Crud", bound=CRUDBase)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class AbstractCRUDService(ABC, Generic[Model, Crud, CreateSchema, UpdateSchema]):
    """
    Abstract base class for a CRUD service.

    This class defines a common interface for services that implement CRUD
    (Create, Read, Update, Delete) operations on objects of type `ModelType`.

    Additionally added the read_all implementation.

    By subclassing this class, you can create a CRUD service that works with
    objects of any type `ModelType`.
    """

    @abstractmethod
    def get(self, uuid: UUID) -> Model | None:
        """
        Retrieve an object from the database.
        :param uuid: the ID of the object to retrieve.
        :returns T: the retrieved object.
        """

    @abstractmethod
    def get_all(self) -> list[Row[Model]] | None:
        """
        Retrieve all objects from the database.
        :returns List[T]: A list of all objects in the database.
        """

    @abstractmethod
    def create(self, obj_in: CreateSchema) -> Model | None:
        """
        Create an object in the database.
        :param obj_in: the object to create.
        :returns T: the created object.
        """

    @abstractmethod
    def update(self, uuid: UUID, obj_in: UpdateSchema) -> Model | None:
        """
        Update an object in the database.
        :param uuid: the ID of the object to update.
        :param obj_in: the updated object.
        :returns T: the updated object.
        """

    @abstractmethod
    def remove(self, uuid: UUID | None) -> Model | None:
        """
        Delete an object from the database.
        :param uuid: The ID of the object to delete.
        """


class CrudServiceBase(AbstractCRUDService[Model, Crud, CreateSchema, UpdateSchema]):
    """
    This is a base class for implementing a CRUD (Create, Read, Update, Delete) service with methods
    for creating, reading, reading all, updating and deleting objects.

    It's a generic class that takes three type parameters:

    ModelType which represents the type of objects being stored in the database,
    CreateSchema which represents the input data for creating objects, and
    UpdateSchema which represents the input data for updating objects.
    """

    def __init__(self, crud: Crud):
        self.crud: Crud = crud

    def get(self, uuid: UUID | str) -> Model | None:
        return self.crud.get(uuid)

    def get_all(self) -> list[Row[Model]] | None:
        all_objects = self.crud.get_all()
        if len(all_objects) == 0:
            return None
        return all_objects

    def create(self, obj_in: CreateSchema) -> Model | None:
        return self.crud.create(obj_in)

    def update(self, uuid: UUID | str, obj_in: UpdateSchema) -> Model | None:
        obj_to_update = self.get(uuid)
        if obj_to_update is None:
            return None
        return self.crud.update(db_obj=obj_to_update, obj_in=obj_in)

    def remove(self, uuid: UUID | str | None) -> Model | None:
        return self.crud.remove(uuid)
