"""
This module defines the CRUD operations for the Calendar model, including an
abstract base class (AbstractCRUDCalendar) and a concrete implementation (CRUDCalendar)
using SQLAlchemy.
"""
from abc import ABC, abstractmethod

from sqlalchemy import Row
from sqlalchemy.orm import Session
from models import CalendarModel
from schemas import CalendarCreate, CalendarUpdate

from crud import CRUDBase


class AbstractCRUDCalendar(CRUDBase[
                               CalendarModel,
                               CalendarCreate,
                               CalendarUpdate
                           ], ABC):
    """
    Abstract class for CRUD operations specific to the Calendar model.
    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Calendar instances.
    """

    @abstractmethod
    def get_by_reservation_type(self, reservation_type: str,
                                include_removed: bool = False) -> CalendarModel | None:
        """
        Retrieves a Calendar instance by its reservation type.

        :param reservation_type: The reservation type of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    def get_by_reservation_service_id(
            self, reservation_service_id: str,
            include_removed: bool = False
    ) -> list[Row[CalendarModel]] | None:
        """
        Retrieves a Calendars instance by its reservation service id.

        :param reservation_service_id: reservation service id of the calendars.
        :param include_removed: Include removed object or not.

        :return: Calendars with reservation service id equal
        to reservation service id or None if no such calendars exists.
        """


class CRUDCalendar(AbstractCRUDCalendar):
    """
    Concrete class for CRUD operations specific to the Calendar model.
    It extends the abstract AbstractCRUDCalendar class and implements the required methods
    for querying and manipulating Calendar instances.
    """

    def __init__(self, db: Session):
        super().__init__(CalendarModel, db)

    def get_by_reservation_type(self, reservation_type: str,
                                include_removed: bool = False) -> CalendarModel | None:
        return self.db.query(self.model) \
            .execution_options(include_deleted=include_removed) \
            .filter(self.model.reservation_type == reservation_type) \
            .first()

    def get_by_reservation_service_id(
            self, reservation_service_id: str,
            include_removed: bool = False
    ) -> list[Row[CalendarModel]] | None:
        return self.db.query(self.model) \
            .execution_options(include_deleted=include_removed) \
            .filter(self.model.reservation_service_id == reservation_service_id) \
            .all()
