"""
This module defines an abstract base class AbstractCalendarService that work with Calendar
"""
from typing import Annotated, Type, List
from fastapi import Depends
from uuid import UUID
from db import get_db
from abc import ABC, abstractmethod
from crud import CRUDCalendar
from services import CrudServiceBase
from models import CalendarModel
from schemas import CalendarCreate, CalendarUpdate
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
    def get_by_reservation_type(self, reservation_type: str) -> CalendarModel:
        """
        Retrieves a Calendar instance by its reservation_type.

        :param reservation_type: The reservation type of the Calendar.
        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    def get_by_service_name(self, service_name: str) -> list[Type[CalendarModel]]:
        """
        Retrieves a Calendar instance by its reservation_type.

        :param service_name: The service name of the Calendar.
        :return: The Calendar instance if found, None otherwise.
        """


class CalendarService(AbstractCalendarService):
    """
    Class UserService represent service that work with User
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        super().__init__(CRUDCalendar(db))

    def create_calendar(self, calendar_create: CalendarCreate) -> CalendarModel | None:
        calendar_create.collision_with_calendar.append(calendar_create.calendar_id)

        calendars_collision = self.get_by_service_name(calendar_create.service_name)

        for collision in calendars_collision:
            calendar_create.collision_with_calendar.append(str(collision.calendar_id))
            collision_with_calendar_exist = collision.collision_with_calendar
            collision_with_calendar_exist.append(calendar_create.calendar_id)
            update_exist_calendar = CalendarUpdate(
                collision_with_calendar=collision_with_calendar_exist
            )
            test_calendar = self.get_by_reservation_type(str(collision.reservation_type))
            self.update(test_calendar.uuid, update_exist_calendar)

        calendar_db = self.create(calendar_create)

        return calendar_db

    def delete_calendar(self, reservation_type) -> CalendarModel | None:
        calendar = self.get_by_reservation_type(reservation_type)
        return self.remove(calendar.uuid)

    def get_by_reservation_type(self, reservation_type: str) -> CalendarModel:
        return self.crud.get_by_reservation_type(reservation_type)

    def get_by_service_name(self, service_name: str) -> List[Type[CalendarModel]]:
        return self.crud.get_by_service_name(service_name)
