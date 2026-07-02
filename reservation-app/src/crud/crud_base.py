"""
Provide an abstract CRUD base class.

Includes a concrete implementation for handling common database operations with
SQLAlchemy and FastAPI.
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, TypeVar
from uuid import UUID

from domain.models.base import Base
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

Model = TypeVar("Model", bound=Base)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class AbstractCRUDBase[Model, CreateSchema, UpdateSchema](ABC):
    """An abstract base class that provides generic CRUD operations."""

    @abstractmethod
    async def get(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> Model | None:
        """
        Retrieve a single record by its id_.

        If include_removed is True retrieve a single record
        including marked as deleted.
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

        If include_removed is True retrieve all records
        including marked as deleted.
        """

    @abstractmethod
    async def create(self, obj_in: CreateSchema) -> Model:
        """Create a new record from the input scheme."""

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
        """Update an existing record with the input scheme."""

    @abstractmethod
    async def restore(
        self,
        obj: Model,
    ) -> Model:
        """Retrieve removed object from soft removed."""

    @abstractmethod
    async def remove(self, id_: UUID) -> None:
        """Remove a record by its id_."""

    @abstractmethod
    async def soft_remove(self, obj: Model) -> Model:
        """
        Soft remove a record by its id_.

        Change attribute deleted_at to time of deletion
        """

    @abstractmethod
    async def count(self, *, include_removed: bool = False) -> int:
        """
        Count the total number of records in the table.

        :param include_removed: whether to include soft-deleted records
        :return: total count as integer
        """


class CRUDBase(AbstractCRUDBase[Model, CreateSchema, UpdateSchema]):
    """
    A concrete implementation of the abstract CRUD base class.

    Handling common database operations with SQLAlchemy and FastAPI.
    """

    def __init__(self, model: type[Model], db: AsyncSession):
        self.model: type[Model] = model
        self.db: AsyncSession = db

    async def get(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> Model | None:
        stmt = (
            select(self.model)
            .execution_options(include_deleted=include_removed)
            .filter(self.model.id == id_)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_list(
        self, skip: int = 0, limit: int = 10, *, include_removed: bool = False
    ) -> list[Model]:
        stmt = (
            select(self.model)
            .execution_options(include_deleted=include_removed)
            .order_by(self.model.id.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self, include_removed: bool = False) -> list[Model]:
        stmt = select(self.model).execution_options(include_deleted=include_removed)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: CreateSchema | dict[str, Any]) -> Model:
        obj_in_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def create_bulk(self, objs_in: list[CreateSchema]) -> list[Model]:
        if not objs_in:
            return []

        db_objs = [self.model(**obj_in.model_dump()) for obj_in in objs_in]

        self.db.add_all(db_objs)
        await self.db.flush()
        await self.db.commit()
        return db_objs

    async def update(
        self,
        *,
        db_obj: Model,
        obj_in: UpdateSchema | dict[str, Any],
    ) -> Model:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def restore(
        self,
        obj: Model,
    ) -> Model:
        obj.deleted_at = None
        self.db.add(obj)
        await self.db.commit()
        return obj

    async def remove(self, id_: UUID) -> None:
        stmt = (
            select(self.model).execution_options(include_deleted=True).filter(self.model.id == id_)
        )
        result = await self.db.execute(stmt)
        obj = result.scalar_one()
        await self.db.delete(obj)
        await self.db.commit()

    async def soft_remove(self, obj: Model) -> Model:
        obj.deleted_at = datetime.now(UTC)
        self.db.add(obj)
        await self.db.commit()
        stmt = (
            select(self.model)
            .execution_options(include_deleted=True)
            .filter(self.model.id == obj.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def count(self, *, include_removed: bool = False) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .execution_options(include_deleted=include_removed)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
