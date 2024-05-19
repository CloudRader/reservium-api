"""
This module defines an abstract base class AbstractCalendarService that work with Calendar
"""
from typing import Annotated, Type, List
from fastapi import Depends
from db import get_db
from abc import ABC, abstractmethod
from crud import CRUDCalendar
from services import CrudServiceBase
from models import CalendarModel
from schemas import CalendarCreate, CalendarUpdate, Rules
from sqlalchemy.orm import Session


class AbstractCalendarService(CrudServiceBase[
                                  CalendarModel,
                                  CRUDCalendar,
                                  CalendarCreate,
                                  CalendarUpdate,
                              ], ABC):
    """
    This abstract class defines the interface for a user service
    that provides CRUD operations for a specific UserModel.
    """

    @abstractmethod
    def create_calendar(self, calendar_create) -> CalendarModel | None:
        """
        Create a User in the database.

        :param calendar_create: CalendarCreate Schema for create.
        :return: the created Calendar.
        """

    @abstractmethod
    def delete_calendar(self, reservation_type) -> CalendarModel | None:
        """
        Create a User in the database.

        :param reservation_type: The reservation type of the Calendar.
        :return: the deleted Calendar.
        """

    @abstractmethod
    def get_by_reservation_type(self, reservation_type: str) -> CalendarModel | None:
        """
        Retrieves a Calendar instance by its reservation_type.

        :param reservation_type: The reservation type of the Calendar.
        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    def get_by_service_alias(self, service_alias: str) -> list[Type[CalendarModel]] | None:
        """
        Retrieves a Calendar instance by its service_alias.

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


class CalendarService(AbstractCalendarService):
    """
    Class UserService represent service that work with User
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        super().__init__(CRUDCalendar(db))

    def create_calendar(self, calendar_create: CalendarCreate) -> CalendarModel | None:
        if self.get(calendar_create.calendar_id) or \
                self.get_by_reservation_type(calendar_create.reservation_type):
            return None

        for collision in calendar_create.collision_with_calendar:
            collision_calendar_to_update = set(self.get(collision).collision_with_calendar)
            collision_calendar_to_update.add(calendar_create.calendar_id)
            update_exist_calendar = CalendarUpdate(
                collision_with_calendar=list(collision_calendar_to_update)
            )
            self.update(collision, update_exist_calendar)

        if calendar_create.collision_with_itself:
            calendar_create.collision_with_calendar.append(calendar_create.calendar_id)

        return self.create(calendar_create)

    def delete_calendar(self, calendar_id) -> CalendarModel | None:
        calendar = self.get_by_calendar_id(calendar_id)
        if calendar is None:
            return None
        return self.crud.remove(calendar_id)

    def get_by_reservation_type(self, reservation_type: str) -> CalendarModel | None:
        return self.crud.get_by_reservation_type(reservation_type)

    def get_by_service_alias(self, service_alias: str) -> List[Type[CalendarModel]] | None:
        return self.crud.get_by_service_alias(service_alias)

    def get_by_calendar_id(self, calendar_id: str) -> CalendarModel | None:
        return self.crud.get_by_calendar_id(calendar_id)
