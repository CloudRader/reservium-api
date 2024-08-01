"""
This module defines the CRUD operations for the MiniService model, including an
abstract base class (AbstractCRUDMiniService) and a concrete implementation (CRUDMiniService)
using SQLAlchemy.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
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
    def get_by_name(self, name: str,
                    include_removed: bool = False) -> MiniServiceModel | None:
        """
        Retrieves a Calendar instance by its name.

        :param name: The name of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance if found, None otherwise.
        """

    @abstractmethod
    def get_names_by_reservation_service_uuid(
            self, reservation_service_uuid: UUID
    ) -> list[str]:
        """
        Retrieves all names from all Mini Services
        by reservation service uuid.

        :param reservation_service_uuid: The uuid of the reservation service.

        :return: list of aliases.
        """


class CRUDMiniService(AbstractCRUDMiniService):
    """
    Concrete class for CRUD operations specific to the Calendar model.
    It extends the abstract AbstractCRUDCalendar class and implements the required methods
    for querying and manipulating Calendar instances.
    """

    def __init__(self, db: Session):
        super().__init__(MiniServiceModel, db)

    def get_by_name(self, name: str,
                    include_removed: bool = False) -> MiniServiceModel | None:
        return self.db.query(self.model) \
            .execution_options(include_deleted=include_removed) \
            .filter(self.model.name == name) \
            .first()

    def get_names_by_reservation_service_uuid(
            self, reservation_service_uuid: UUID
    ) -> list[str]:
        stmt = select(self.model.name).where(
            self.model.reservation_service_uuid == reservation_service_uuid
        )
        result = self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]
