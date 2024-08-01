"""
This module defines the CRUD operations for the ReservationService model, including an
abstract base class (AbstractCRUDReservationService) and a concrete implementation
(CRUDReservationService) using SQLAlchemy.
"""
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.orm import Session
from models import ReservationServiceModel
from schemas import ReservationServiceCreate, ReservationServiceUpdate

from crud import CRUDBase


class AbstractCRUDReservationService(CRUDBase[
                                         ReservationServiceModel,
                                         ReservationServiceCreate,
                                         ReservationServiceUpdate
                                     ], ABC):
    """
    Abstract class for CRUD operations specific to the Calendar model.
    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Calendar instances.
    """

    @abstractmethod
    def get_by_name(self, name: str,
                    include_removed: bool = False) -> ReservationServiceModel | None:
        """
        Retrieves a Reservation Service instance by its name.

        :param name: The name of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    def get_by_alias(self, alias: str,
                     include_removed: bool = False) -> ReservationServiceModel | None:
        """
        Retrieves a Reservation Services instance by its service alias.

        :param alias: The alias of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    def get_all_aliases(self) -> list[str]:
        """
        Retrieves all aliases from all  Reservation Services.

        :return: list of aliases.
        """


class CRUDReservationService(AbstractCRUDReservationService):
    """
    Concrete class for CRUD operations specific to the Calendar model.
    It extends the abstract AbstractCRUDCalendar class and implements the required methods
    for querying and manipulating Calendar instances.
    """

    def __init__(self, db: Session):
        super().__init__(ReservationServiceModel, db)

    def get_by_name(self, name: str,
                    include_removed: bool = False) -> ReservationServiceModel | None:
        return self.db.query(self.model) \
            .execution_options(include_deleted=include_removed) \
            .filter(self.model.name == name) \
            .first()

    def get_by_alias(self, alias: str,
                     include_removed: bool = False) -> ReservationServiceModel | None:
        return self.db.query(self.model) \
            .execution_options(include_deleted=include_removed) \
            .filter(self.model.alias == alias) \
            .first()

    def get_all_aliases(self) -> list[str]:
        stmt = select(self.model.alias)
        result = self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]
