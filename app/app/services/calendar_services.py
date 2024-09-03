"""
This module defines an abstract base class AbstractCalendarService that work with Calendar
"""
from typing import Annotated
from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from fastapi import Depends
from db import get_db
from crud import CRUDCalendar, CRUDReservationService, CRUDMiniService
from services import CrudServiceBase
from models import CalendarModel
from schemas import CalendarCreate, CalendarUpdate, User
from api import auth_google
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
    def create_calendar(
            self, calendar_create: CalendarCreate,
            user: User
    ) -> CalendarModel | None:
        """
        Create a Calendar in the database.

        :param calendar_create: CalendarCreate Schema for create.
        :param user: the UserSchema for control permissions of the calendar.

        :return: the created Calendar.
        """

    @abstractmethod
    def update_calendar(
            self, calendar_id: str,
            calendar_update: CalendarUpdate,
            user: User
    ) -> CalendarModel | None:
        """
        Update a Calendar in the database.

        :param calendar_id: The id of the Calendar.
        :param calendar_update: CalendarUpdate Schema for update.
        :param user: the UserSchema for control permissions of the calendar.

        :return: the updated Calendar.
        """

    @abstractmethod
    def delete_calendar(
            self, calendar_id: str,
            user: User
    ) -> CalendarModel | None:
        """
        Delete a Calendar in the database.

        :param calendar_id: The id of the Calendar.
        :param user: the UserSchema for control permissions of the calendar.

        :return: the deleted Calendar.
        """

    @abstractmethod
    def test(
            self, calendar_id
    ):
        """
        Something not impl yet

        :return: Any.
        """

    @abstractmethod
    def get_all_google_calendar_to_add(
            self, user: User
    ) -> list[dict] | None:
        """
        Retrieves a Calendars from Google calendars
        that are candidates for additions

        :param user: the UserSchema for control permissions of the calendar.

        :return: candidate list for additions, None otherwise.
        """

    @abstractmethod
    def get_by_reservation_type(
            self, reservation_type: str,
            include_removed: bool = False
    ) -> CalendarModel | None:
        """
        Retrieves a Calendar instance by its reservation_type.

        :param reservation_type: The reservation type of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    def get_mini_services_by_reservation_type(
            self, calendar_id: str
    ) -> list[str] | None:
        """
        Retrieves a list mini services instance by its reservation_type.

        :param calendar_id: The id of the Calendar.

        :return: The str of mini services if found, None otherwise.
        """


class CalendarService(AbstractCalendarService):
    """
    Class CalendarService represent service that work with Calendar
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.google_calendar_service = build("calendar", "v3", credentials=auth_google(None))
        self.reservation_service_crud = CRUDReservationService(db)
        self.mini_service_crud = CRUDMiniService(db)
        super().__init__(CRUDCalendar(db))

    def create_calendar(
            self, calendar_create: CalendarCreate,
            user: User
    ) -> CalendarModel | None:
        if self.get(calendar_create.id, True) or \
                self.get_by_reservation_type(calendar_create.reservation_type, True):
            return None

        reservation_service = self.reservation_service_crud.get(
            calendar_create.reservation_service_id
        )

        if user is None or reservation_service is None or \
                reservation_service.alias not in user.roles:
            return None

        for mini_service in calendar_create.mini_services:
            if mini_service not in \
                    self.mini_service_crud.get_names_by_reservation_service_uuid(
                        reservation_service.id):
                return None

        if calendar_create.collision_with_calendar is not None:
            for collision in calendar_create.collision_with_calendar:
                if not self.get(collision):
                    return None
                collision_calendar_to_update = set(self.get(collision).collision_with_calendar)
                collision_calendar_to_update.add(calendar_create.id)
                update_exist_calendar = CalendarUpdate(
                    collision_with_calendar=list(collision_calendar_to_update)
                )
                if not self.update(collision, update_exist_calendar):
                    return None

        return self.create(calendar_create)

    def update_calendar(
            self, calendar_id: str,
            calendar_update: CalendarUpdate,
            user: User
    ) -> CalendarModel | None:
        calendar_to_update = self.get(calendar_id)

        if calendar_to_update is None:
            return None

        reservation_service = self.reservation_service_crud.get(
            calendar_to_update.reservation_service_id
        )

        if user is None or reservation_service is None or \
                reservation_service.alias not in user.roles:
            return None

        return self.update(calendar_id, calendar_update)

    def delete_calendar(
            self, calendar_id: str,
            user: User
    ) -> CalendarModel | None:
        calendar = self.get(calendar_id)

        if calendar is None:
            return None

        reservation_service = self.reservation_service_crud.get(
            calendar.reservation_service_id
        )

        if user is None or reservation_service is None or \
                reservation_service.alias not in user.roles:
            return None

        for calendar_to_update in reservation_service.calendars:
            if calendar_to_update.collision_with_calendar and \
                    calendar.id in calendar_to_update.collision_with_calendar:
                collision_to_update = calendar_to_update.collision_with_calendar.copy()
                collision_to_update.remove(calendar.id)
                update_exist_calendar = CalendarUpdate(
                    collision_with_calendar=collision_to_update
                )
                self.update(calendar_to_update.id, update_exist_calendar)

        return self.crud.soft_remove(calendar_id)

    # pylint: disable=no-member
    # reason: The googleapiclient.discovery.build function
    # dynamically creates the events attribute, which is not easily
    # understood by static code analysis tools like pylint.
    def test(
            self, calendar_id
    ):
        test = self.google_calendar_service.events().list(
            calendarId=calendar_id,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        # event = self.google_calendar_service.events().get(
        #     calendarId=calendar_id, eventId="1lnut6920f7sesr6spc1veliss"
        # ).execute()

        return test

    def get_all_google_calendar_to_add(
            self, user: User
    ) -> list[dict] | None:
        if len(user.roles) < 1:
            return None

        google_calendars = self.google_calendar_service. \
            calendarList().list().execute()

        new_calendar_candidates = []

        for calendar in google_calendars.get('items', []):
            if calendar.get('accessRole') == 'owner' and not \
                    calendar.get('primary', False):
                if self.get(calendar.get('id', None)) is None:
                    new_calendar_candidates.append(calendar)

        return new_calendar_candidates

    def get_by_reservation_type(
            self, reservation_type: str,
            include_removed: bool = False
    ) -> CalendarModel | None:
        return self.crud.get_by_reservation_type(
            reservation_type, include_removed)

    def get_mini_services_by_reservation_type(
            self, calendar_id: str
    ) -> list[str] | None:
        calendar = self.crud.get(calendar_id)

        if calendar is None:
            return None

        return calendar.mini_services
