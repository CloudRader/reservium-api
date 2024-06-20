"""
This module defines an abstract base class AbstractCalendarService that work with Calendar
"""
from typing import Annotated, Type, List
from abc import ABC, abstractmethod
from fastapi import Depends
from db import get_db
from crud import CRUDCalendar
from services import CrudServiceBase
from models import CalendarModel
from schemas import CalendarCreate, CalendarUpdate, User
from sqlalchemy.orm import Session


class AbstractCalendarService(CrudServiceBase[
                                  CalendarModel,
                                  CRUDCalendar,
                                  CalendarCreate,
                                  CalendarUpdate,
                              ], ABC):
    """
    This abstract class defines the interface for a calendar service
    that provides CRUD operations for a specific CalendarModel.
    """

    @abstractmethod
    def create_calendar(self, calendar_create,
                        user: User) -> CalendarModel | None:
        """
        Create a Calendar in the database.

        :param calendar_create: CalendarCreate Schema for create.
        :param user: the UserSchema for control permissions of the calendar.

        :return: the created Calendar.
        """

    @abstractmethod
    def update_calendar(self, calendar_id, calendar_update,
                        user: User) -> CalendarModel | None:
        """
        Update a Calendar in the database.

        :param calendar_id: The calendar id of the Calendar.
        :param calendar_update: CalendarUpdate Schema for update.
        :param user: the UserSchema for control permissions of the calendar.

        :return: the updated Calendar.
        """

    @abstractmethod
    def delete_calendar(self, calendar_id, user: User) -> CalendarModel | None:
        """
        Delete a Calendar in the database.

        :param calendar_id: The calendar id of the Calendar.
        :param user: the UserSchema for control permissions of the calendar.

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
    def get_reservation_type_by_service_alias(self, service_alias: str
                                              ) -> list[str] | None:
        """
        Retrieves a list reservation types instance by its service_alias.

        :param service_alias: The service alias of the Calendar.

        :return: The str of reservation types if found, None otherwise.
        """

    @abstractmethod
    def get_mini_services_by_reservation_type(self, reservation_type: str
                                              ) -> list[str] | None:
        """
        Retrieves a list mini services instance by its reservation_type.

        :param reservation_type: The reservation type of the Calendar.

        :return: The str of mini services if found, None otherwise.
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
    Class CalendarService represent service that work with Calendar
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        super().__init__(CRUDCalendar(db))

    def create_calendar(self, calendar_create: CalendarCreate,
                        user: User) -> CalendarModel | None:
        if self.get(calendar_create.calendar_id) or \
                self.get_by_reservation_type(calendar_create.reservation_type):
            return None

        if user is None or calendar_create.service_alias not in user.roles:
            return None

        if calendar_create.collision_with_calendar is not None:
            for collision in calendar_create.collision_with_calendar:
                if not self.get_by_calendar_id(collision):
                    return None
                collision_calendar_to_update = set(self.get(collision).collision_with_calendar)
                collision_calendar_to_update.add(calendar_create.calendar_id)
                update_exist_calendar = CalendarUpdate(
                    collision_with_calendar=list(collision_calendar_to_update)
                )
                if not self.update(collision, update_exist_calendar):
                    return None

        if calendar_create.collision_with_itself:
            calendar_create.collision_with_calendar.append(calendar_create.calendar_id)

        return self.create(calendar_create)

    def update_calendar(self, calendar_id, calendar_update,
                        user: User) -> CalendarModel | None:
        calendar_to_update = self.get_by_calendar_id(calendar_id)

        if calendar_to_update is None or user is None or \
                calendar_to_update.service_alias not in user.roles:
            return None

        return self.update(calendar_id, calendar_update)

    def delete_calendar(self, calendar_id, user: User) -> CalendarModel | None:
        calendar = self.get_by_calendar_id(calendar_id)
        if calendar is None:
            return None

        if user is None or calendar.service_alias not in user.roles:
            return None

        calendars = self.get_by_service_alias(calendar.service_alias)

        if calendars is None:
            return None

        for calendar_to_update in calendars:
            if calendar_to_update.collision_with_calendar and \
                    calendar.calendar_id in calendar_to_update.collision_with_calendar:
                collision_to_update = calendar_to_update.collision_with_calendar.copy()
                collision_to_update.remove(calendar.calendar_id)
                update_exist_calendar = CalendarUpdate(
                    collision_with_calendar=collision_to_update
                )
                self.update(calendar_to_update.calendar_id, update_exist_calendar)

        return self.crud.remove(calendar_id)

    def get_by_reservation_type(self, reservation_type: str) -> CalendarModel | None:
        return self.crud.get_by_reservation_type(reservation_type)

    def get_by_service_alias(self, service_alias: str) -> List[Type[CalendarModel]] | None:
        return self.crud.get_by_service_alias(service_alias)

    def get_reservation_type_by_service_alias(self, service_alias: str
                                              ) -> list[str] | None:
        calendars = self.get_by_service_alias(service_alias)

        if calendars is None:
            return None

        reservation_types: list[str] = []
        for calendar in calendars:
            reservation_types.append(calendar.reservation_type)

        if not reservation_types:
            return None

        return reservation_types

    def get_mini_services_by_reservation_type(self, reservation_type: str
                                              ) -> list[str] | None:
        calendar = self.get_by_reservation_type(reservation_type)

        if calendar is None or not calendar.mini_services:
            return None

        return calendar.mini_services

    def get_by_calendar_id(self, calendar_id: str) -> CalendarModel | None:
        return self.crud.get_by_calendar_id(calendar_id)
