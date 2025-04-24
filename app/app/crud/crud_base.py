"""
This module provides an abstract CRUD base class and a concrete implementation
for handling common database operations with SQLAlchemy and FastAPI.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TypeVar, Generic, Type, Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import Base

Model = TypeVar("Model", bound=Base)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class AbstractCRUDBase(Generic[Model, CreateSchema, UpdateSchema], ABC):
    """
   An abstract base class that provides generic CRUD operations.
   """

    @abstractmethod
    async def get(self, uuid: UUID | str | int,
                  include_removed: bool = False) -> Model | None:
        """
        Retrieve a single record by its UUID.
        If include_removed is True retrieve a single record
        including marked as deleted.
        """

    @abstractmethod
    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[Model]:
        """
        Retrieve a list of records with pagination.
        """

    @abstractmethod
    async def get_all(self, include_removed: bool = False) -> list[Model]:
        """
        Retrieve all records without pagination.
        If include_removed is True retrieve all records
        including marked as deleted.
        """

    @abstractmethod
    async def get_by_reservation_service_id(
            self, reservation_service_id: str,
            include_removed: bool = False
    ) -> list[Model] | None:
        """
        Retrieves all records by its reservation service id.
        If include_removed is True retrieve all records
        including marked as deleted.
        """

    @abstractmethod
    async def create(self, obj_in: CreateSchema) -> Model:
        """
        Create a new record from the input scheme.
        """

    @abstractmethod
    async def update(self, *, db_obj: Model | None, obj_in: UpdateSchema) -> Model | None:
        """
        Update an existing record with the input scheme.
        """

    @abstractmethod
    async def retrieve_removed_object(self, uuid: UUID | str | int | None
                                ) -> Model | None:
        """
        Retrieve removed object from soft removed.
        """

    @abstractmethod
    async def remove(self, uuid: UUID | str | int | None) -> Model | None:
        """
        Remove a record by its UUID.
        """

    @abstractmethod
    async def soft_remove(self, uuid: UUID | str | int | None) -> Model | None:
        """
        Soft remove a record by its UUID.
        Change attribute deleted_at to time of deletion
        """


class CRUDBase(AbstractCRUDBase[Model, CreateSchema, UpdateSchema]):
    """
    A concrete implementation of the abstract CRUD base class for handling
    common database operations with SQLAlchemy and FastAPI.
    """

    def __init__(self, model: Type[Model], db: AsyncSession):
        self.model: Type[Model] = model
        self.db: AsyncSession = db

    async def get(self, uuid: UUID | str | int,
                  include_removed: bool = False) -> Model | None:
        if uuid is None:
            return None
        stmt = select(self.model).filter(self.model.id == uuid)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[Model]:
        stmt = select(self.model).order_by(self.model.id.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self, include_removed: bool = False) -> list[Model]:
        stmt = select(self.model).execution_options(include_deleted=include_removed)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_reservation_service_id(
            self, reservation_service_id: UUID | str,
            include_removed: bool = False
    ) -> list[Model] | None:
        stmt = select(self.model).filter(
            self.model.reservation_service_id == reservation_service_id)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: CreateSchema | dict[str, Any]) -> Model:
        obj_in_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, *,
                     db_obj: Model | None,
                     obj_in: UpdateSchema | dict[str, Any]) -> Model | None:
        if db_obj is None or obj_in is None:
            return None

        db_obj_data = jsonable_encoder(db_obj)
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)

        for field in db_obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def retrieve_removed_object(self, uuid: UUID | str | int | None
                                ) -> Model | None:
        if uuid is None:
            return None
        stmt = (select(self.model).execution_options(include_deleted=True)
                .filter(self.model.id == uuid))
        result = await self.db.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        obj.deleted_at = None
        self.db.add(obj)
        await self.db.commit()
        return obj

    async def remove(self, uuid: UUID | str | int | None) -> Model | None:
        stmt = (select(self.model)
                .execution_options(include_deleted=True)
                .filter(self.model.id == uuid))
        result = await self.db.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        await self.db.delete(obj)
        await self.db.commit()
        return obj

    async def soft_remove(self, uuid: UUID | str | int | None) -> Model | None:
        if uuid is None:
            return None
        stmt = select(self.model).filter(self.model.id == uuid)
        result = await self.db.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None or obj.deleted_at is not None:
            return None
        obj.deleted_at = datetime.now(timezone.utc)
        self.db.add(obj)
        await self.db.commit()
        stmt = (select(self.model).execution_options(include_deleted=True)
                .filter(self.model.id == uuid))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
