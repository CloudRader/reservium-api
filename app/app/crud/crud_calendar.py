"""
This module defines the CRUD operations for the Calendar model, including an
abstract base class (AbstractCRUDCalendar) and a concrete implementation (CRUDCalendar)
using SQLAlchemy.
"""
from abc import ABC, abstractmethod
from typing import Type

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
    def get_by_reservation_type(self, reservation_type: str) -> CalendarModel | None:
        """
        Retrieves a Calendar instance by its reservation type.

        :param reservation_type: The reservation type of the Calendar.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    def get_by_service_alias(self, service_alias: str) -> list[Type[CalendarModel]]:
        """
        Retrieves a Calendar instance by its service alias.

        :param service_alias: The service alias of the Calendar.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    def get_by_calendar_id(self, calendar_id: str) -> CalendarModel | None:
        """
        Retrieves a Calendar instance by its calendar id.

        :param calendar_id: The calendar id of the Calendar.

        :return: The Calendar instance if found, None otherwise.
        """


class CRUDCalendar(AbstractCRUDCalendar):
    """
    Concrete class for CRUD operations specific to the Calendar model.
    It extends the abstract AbstractCRUDCalendar class and implements the required methods
    for querying and manipulating Calendar instances.
    """

    def __init__(self, db: Session):
        super().__init__(CalendarModel, db)

    def get_by_reservation_type(self, reservation_type: str) -> CalendarModel | None:
        return self.db.query(self.model) \
            .filter(self.model.reservation_type == reservation_type) \
            .first()

    def get_by_service_alias(self, service_alias: str) -> list[Type[CalendarModel]]:
        return self.db.query(self.model) \
            .filter(self.model.service_alias == service_alias) \
            .all()

    def get_by_calendar_id(self, calendar_id: str) -> CalendarModel | None:
        return self.db.query(self.model) \
            .filter(self.model.calendar_id == calendar_id) \
            .first()
