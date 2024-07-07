"""
This module defines the CRUD operations for the MiniService model, including an
abstract base class (AbstractCRUDMiniService) and a concrete implementation (CRUDMiniService)
using SQLAlchemy.
"""
from abc import ABC, abstractmethod
from typing import Type

from sqlalchemy.orm import Session
from models import MiniServiceModel
from schemas import MiniServiceCreate, MiniServiceUpdate

from crud import CRUDBase


class AbstractCRUDMiniService(CRUDBase[
                                  MiniServiceModel,
                                  MiniServiceCreate,
                                  MiniServiceUpdate
                              ], ABC):
    """
    Abstract class for CRUD operations specific to the Calendar model.
    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Calendar instances.
    """

    @abstractmethod
    def get_by_name(self, name: str) -> MiniServiceModel | None:
        """
        Retrieves a Calendar instance by its name.

        :param name: The name of the Mini Service.

        :return: The Mini Service instance if found, None otherwise.
        """


class CRUDMiniService(AbstractCRUDMiniService):
    """
    Concrete class for CRUD operations specific to the Calendar model.
    It extends the abstract AbstractCRUDCalendar class and implements the required methods
    for querying and manipulating Calendar instances.
    """

    def __init__(self, db: Session):
        super().__init__(MiniServiceModel, db)

    def get_by_name(self, name: str) -> MiniServiceModel | None:
        return self.db.query(self.model) \
            .filter(self.model.name == name) \
            .first()
