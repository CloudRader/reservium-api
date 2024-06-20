"""
This module provides an abstract CRUD base class and a concrete implementation
for handling common database operations with SQLAlchemy and FastAPI.
"""
from abc import ABC, abstractmethod
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
    def get(self, uuid: UUID | str) -> Model | None:
        """
        Retrieve a single record by its UUID.
        """

    @abstractmethod
    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Row[Model]]:
        """
        Retrieve a list of records with pagination.
        """

    @abstractmethod
    def get_all(self) -> list[Row[Model]]:
        """
        Retrieve all records without pagination.
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
    def remove(self, uuid: UUID | str | None) -> Model | None:
        """
        Remove a record by its UUID.
        """


class CRUDBase(AbstractCRUDBase[Model, CreateSchema, UpdateSchema]):
    """
    A concrete implementation of the abstract CRUD base class for handling
    common database operations with SQLAlchemy and FastAPI.
    """

    def __init__(self, model: Type[Model], db: Session):
        self.model: Type[Model] = model
        self.db: Session = db

    def get(self, uuid: UUID | str) -> Model | None:
        if uuid is None:
            return None
        return self.db.get(self.model, uuid)

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[Row[Model]]:
        return self.db.query(self.model).order_by(self.model.submitted_at.desc()) \
            .offset(skip).limit(limit).all()

    def get_all(self) -> list[Row[Model]]:
        return self.db.query(self.model).all()

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

    def remove(self, uuid: UUID | str | None) -> Model | None:
        if uuid is None:
            return None
        obj = self.db.get(self.model, uuid)
        if obj is None:
            return None
        self.db.delete(obj)
        self.db.commit()
        return obj
