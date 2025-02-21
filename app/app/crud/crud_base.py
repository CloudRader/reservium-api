"""
This module provides an abstract CRUD base class and a concrete implementation
for handling common database operations with SQLAlchemy and FastAPI.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar, Generic, Type, Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import Row
from sqlalchemy.orm import Session

from db import Base

Model = TypeVar("Model", bound=Base)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class AbstractCRUDBase(Generic[Model, CreateSchema, UpdateSchema], ABC):
    """
   An abstract base class that provides generic CRUD operations.
   """

    @abstractmethod
    def get(self, uuid: UUID | str | int,
            include_removed: bool = False) -> Model | None:
        """
        Retrieve a single record by its UUID.
        If include_removed is True retrieve a single record
        including marked as deleted.
        """

    @abstractmethod
    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Row[Model]]:
        """
        Retrieve a list of records with pagination.
        """

    @abstractmethod
    def get_all(self, include_removed: bool = False) -> list[Row[Model]]:
        """
        Retrieve all records without pagination.
        If include_removed is True retrieve all records
        including marked as deleted.
        """

    @abstractmethod
    def get_by_reservation_service_id(
            self, reservation_service_id: str,
            include_removed: bool = False
    ) -> list[Row[Model]] | None:
        """
        Retrieves all records by its reservation service id.
        If include_removed is True retrieve all records
        including marked as deleted.
        """

    @abstractmethod
    def create(self, obj_in: CreateSchema) -> Model:
        """
        Create a new record from the input scheme.
        """

    @abstractmethod
    def update(self, *, db_obj: Model | None, obj_in: UpdateSchema) -> Model | None:
        """
        Update an existing record with the input scheme.
        """

    @abstractmethod
    def retrieve_removed_object(self, uuid: UUID | str | int | None
                                ) -> Model | None:
        """
        Retrieve removed object from soft removed.
        """

    @abstractmethod
    def remove(self, uuid: UUID | str | int | None) -> Model | None:
        """
        Remove a record by its UUID.
        """

    @abstractmethod
    def soft_remove(self, uuid: UUID | str | int | None) -> Model | None:
        """
        Soft remove a record by its UUID.
        Change attribute deleted_at to time of deletion
        """


class CRUDBase(AbstractCRUDBase[Model, CreateSchema, UpdateSchema]):
    """
    A concrete implementation of the abstract CRUD base class for handling
    common database operations with SQLAlchemy and FastAPI.
    """

    def __init__(self, model: Type[Model], db: Session):
        self.model: Type[Model] = model
        self.db: Session = db

    def get(self, uuid: UUID | str | int,
            include_removed: bool = False) -> Model | None:
        if uuid is None:
            return None
        return self.db.query(self.model) \
            .execution_options(include_deleted=include_removed) \
            .filter(self.model.id == uuid).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Row[Model]]:
        return self.db.query(self.model).order_by(self.model.submitted_at.desc()) \
            .offset(skip).limit(limit).all()

    def get_all(self, include_removed: bool = False) -> list[Row[Model]]:
        return self.db.query(self.model) \
            .execution_options(include_deleted=include_removed).all()

    def get_by_reservation_service_id(
            self, reservation_service_id: UUID | str,
            include_removed: bool = False
    ) -> list[Row[Model]] | None:
        return self.db.query(self.model) \
            .execution_options(include_deleted=include_removed) \
            .filter(self.model.reservation_service_id == reservation_service_id) \
            .all()

    def create(self, obj_in: CreateSchema | dict[str, Any]) -> Model:
        obj_in_data = obj_in if isinstance(obj_in, dict) else obj_in.dict()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *,
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
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def retrieve_removed_object(self, uuid: UUID | str | int | None
                                ) -> Model | None:
        if uuid is None:
            return None
        obj = self.db.query(self.model) \
            .execution_options(include_deleted=True). \
            filter(self.model.id == uuid).first()
        if obj is None:
            return None
        obj.deleted_at = None
        self.db.add(obj)
        self.db.commit()
        return obj

    def remove(self, uuid: UUID | str | int | None) -> Model | None:
        if uuid is None:
            return None
        # obj = self.db.get(self.model, uuid)
        obj = self.db.query(self.model) \
            .execution_options(include_deleted=True). \
            filter(self.model.id == uuid).first()
        if obj is None:
            return None
        self.db.delete(obj)
        self.db.commit()
        return obj

    def soft_remove(self, uuid: UUID | str | int | None) -> Model | None:
        if uuid is None:
            return None
        obj = self.db.get(self.model, uuid)
        if obj is None or obj.deleted_at is not None:
            return None
        obj.deleted_at = datetime.utcnow()
        self.db.add(obj)
        self.db.commit()
        return self.db.query(self.model) \
            .execution_options(include_deleted=True). \
            filter(self.model.id == uuid).first()
