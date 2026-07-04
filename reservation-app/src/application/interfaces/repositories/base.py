"""
Provide a generic repository interface (port) for CRUD operations.

This module defines the repository port for the application's domain layer,
standardizing the contract for data persistence and retrieval independent
of any specific database infrastructure.
"""

from abc import ABC, abstractmethod
from typing import TypeVar
from uuid import UUID

from domain.models.base import Base
from pydantic import BaseModel

Model = TypeVar("Model", bound=Base)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class RepositoryBase[Model, CreateSchema, UpdateSchema](ABC):
    """
    A generic repository interface defining standard CRUD operations.

    Acting as a port in the domain layer, this interface establishes
    the contract for basic data access patterns, including support for
    pagination and soft-deleted database records.
    """

    @abstractmethod
    async def get(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> Model | None:
        """
        Retrieve a single record by its ID.

        Optionally include records that have been soft-deleted.

        :param id_: The UUID of the record to retrieve.
        :param include_removed: Whether to include soft-deleted records.

        :return: The Model instance if found, otherwise None.
        """

    @abstractmethod
    async def get_list(
        self, skip: int = 0, limit: int = 10, *, include_removed: bool = False
    ) -> list[Model]:
        """
        Retrieve a paginated list of objects from the database.

        Optionally including soft-deleted records.

        :param skip: Number of records to skip (offset).
        :param limit: Maximum number of records to return.
        :param include_removed: Whether to include soft-deleted records.

        :returns: List of Model instances.
        """

    @abstractmethod
    async def get_all(self, include_removed: bool = False) -> list[Model]:
        """
        Retrieve all records without pagination.

        Optionally include records that have been soft-deleted.

        :param include_removed: Whether to include soft-deleted records.

        :return: List of all Model instances.
        """

    @abstractmethod
    async def create(self, obj_in: CreateSchema) -> Model:
        """
        Create a new record from the input schema.

        :param obj_in: The schema containing data for the new record.

        :return: The newly created Model instance.
        """

    @abstractmethod
    async def create_bulk(self, objs_in: list[CreateSchema]) -> list[Model]:
        """
        Create multiple objects in a single transaction.

        :param objs_in: List of objects to create.

        :return: List of created objects.
        """

    @abstractmethod
    async def update(
        self,
        *,
        db_obj: Model,
        obj_in: UpdateSchema,
    ) -> Model:
        """
        Update an existing record with data from the input schema.

        :param db_obj: The existing database model instance to update.
        :param obj_in: The schema containing the updated data.

        :return: The updated Model instance.
        """

    @abstractmethod
    async def restore(
        self,
        obj: Model,
    ) -> Model:
        """
        Restore a previously soft-deleted object.

        :param obj: The soft-deleted model instance to restore.

        :return: The restored Model instance.
        """

    @abstractmethod
    async def remove(self, id_: UUID) -> None:
        """
        Permanently remove a record from the database by its ID.

        :param id_: The UUID of the record to remove.

        :return: None.
        """

    @abstractmethod
    async def soft_remove(self, obj: Model) -> Model:
        """
        Soft-remove a record.

        Marks the record as deleted by updating its deletion timestamp
        without physically removing it from the database.

        :param obj: The model instance to soft-remove.

        :return: The updated Model instance marked as deleted.
        """

    @abstractmethod
    async def count(self, *, include_removed: bool = False) -> int:
        """
        Count the total number of records in the database.

        :param include_removed: Whether to include soft-deleted records in the count.

        :return: The total count of records as an integer.
        """
