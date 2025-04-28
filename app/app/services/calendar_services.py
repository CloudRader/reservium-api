"""
This module defines an abstract base class AbstractCalendarService that work with Calendar
"""
from typing import Annotated
from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import Depends
from api import BaseAppException, PermissionDeniedException
from db import db_session
from crud import CRUDCalendar, CRUDReservationService, CRUDMiniService
from services import CrudServiceBase
from models import CalendarModel, ReservationServiceModel
from schemas import CalendarCreate, CalendarUpdate, User
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession


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
    async def create_calendar(
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
    async def update_calendar(
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
    async def retrieve_removed_object(
            self, uuid: UUID | str | int | None,
            user: User
    ) -> CalendarModel | None:
        """
        Retrieve removed calendar from soft removed.

        :param uuid: The ID of the calendar to retrieve from removed.
        :param user: the UserSchema for control permissions of the calendar.

        :return: the updated Calendar.
        """

    @abstractmethod
    async def delete_calendar(
            self, calendar_id: str,
            user: User,
            hard_remove: bool = False
    ) -> CalendarModel | None:
        """
        Delete a Calendar in the database.

        :param calendar_id: The id of the Calendar.
        :param user: the UserSchema for control permissions of the calendar.
        :param hard_remove: hard remove of the calendar or not.

        :return: the deleted Calendar.
        """

    @abstractmethod
    async def get_all_google_calendar_to_add(
            self, user: User,
            google_calendars: dict,
    ) -> list[dict] | None:
        """
        Retrieves a Calendars from Google calendars
        that are candidates for additions

        :param user: the UserSchema for control permissions of the calendar.
        :param google_calendars: calendars from Google Calendars.

        :return: candidate list for additions, None otherwise.
        """

    @abstractmethod
    async def get_by_reservation_type(
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
    async def get_mini_services_by_calendar(
            self, calendar_id: str
    ) -> list[str] | None:
        """
        Retrieves a list mini services instance by its calendar.

        :param calendar_id: The id of the Calendar.

        :return: The str of mini services if found, None otherwise.
        """

    @abstractmethod
    async def get_reservation_service_of_this_calendar(
            self, reservation_service_id: UUID
    ) -> ReservationServiceModel | None:
        """
        Retrieves the reservation service of this calendar
        by reservation service id.

        :param reservation_service_id: The id of the Reservation Service.

        :return: Reservation Service of this calendar if found, None otherwise.
        """

    @abstractmethod
    async def get_by_reservation_service_id(
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


class CalendarService(AbstractCalendarService):
    """
    Class CalendarService represent service that work with Calendar
    """

    def __init__(self, db: Annotated[
        AsyncSession, Depends(db_session.scoped_session_dependency)]):
        self.reservation_service_crud = CRUDReservationService(db)
        self.mini_service_crud = CRUDMiniService(db)
        super().__init__(CRUDCalendar(db))

    async def create_calendar(
            self, calendar_create: CalendarCreate,
            user: User
    ) -> CalendarModel | None:
        if await self.get(calendar_create.id, True):
            raise BaseAppException("A calendar with this id already exist.")
        if await self.get_by_reservation_type(calendar_create.reservation_type, True):
            raise BaseAppException("A calendar with this reservation type already exist.")

        reservation_service = await self.reservation_service_crud.get(
            calendar_create.reservation_service_id
        )

        if reservation_service is None:
            raise BaseAppException("A reservation service of calendar isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to create calendars."
            )

        if calendar_create.mini_services:
            for mini_service in calendar_create.mini_services:
                if mini_service not in \
                        await self.mini_service_crud.get_names_by_reservation_service_id(
                            reservation_service.id):
                    raise BaseAppException("These mini services do not exist in the db "
                                           "that you want to add to this calendar.")

        if calendar_create.collision_with_calendar is not None:
            for collision in calendar_create.collision_with_calendar:
                existing_calendar = await self.get(collision)
                if existing_calendar is None:
                    raise BaseAppException("These calendar do not exist in the db "
                                           "that you want to add to this calendar collision.")
                collision_calendar_to_update = set(existing_calendar.collision_with_calendar)
                collision_calendar_to_update.add(calendar_create.id)
                update_exist_calendar = CalendarUpdate(
                    collision_with_calendar=list(collision_calendar_to_update)
                )
                if not await self.update(collision, update_exist_calendar):
                    raise BaseAppException("Failed to update collisions on the calendar "
                                           f"with this id {collision}")

        return await self.create(calendar_create)

    async def update_calendar(
            self, calendar_id: str,
            calendar_update: CalendarUpdate,
            user: User
    ) -> CalendarModel | None:
        calendar_to_update = await self.get(calendar_id)

        if calendar_to_update is None:
            return None

        reservation_service = await self.reservation_service_crud.get(
            calendar_to_update.reservation_service_id
        )

        if reservation_service is None:
            raise BaseAppException("A reservation service of calendar isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to create calendars."
            )

        return await self.update(calendar_id, calendar_update)

    async def retrieve_removed_object(
            self, uuid: UUID | str | int | None,
            user: User
    ) -> CalendarModel | None:
        calendar = await self.get(uuid, True)

        if calendar.deleted_at is None:
            raise BaseAppException("A calendar was not soft deleted.")

        reservation_service = await self.reservation_service_crud.get(
            str(calendar.reservation_service_id)
        )

        if reservation_service is None:
            raise BaseAppException("A reservation service of calendar isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to create calendars."
            )

        return await self.crud.retrieve_removed_object(uuid)

    async def delete_calendar(
            self, calendar_id: str,
            user: User,
            hard_remove: bool = False
    ) -> CalendarModel | None:
        calendar = await self.get(calendar_id, True)

        if calendar is None:
            return None

        if hard_remove and not user.section_head:
            raise PermissionDeniedException(
                "You must be the head of PS to totally delete calendars.")

        reservation_service = await self.reservation_service_crud.get(
            calendar.reservation_service_id
        )

        if reservation_service is None:
            raise BaseAppException("A reservation service of calendar isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to create calendars."
            )

        for calendar_to_update in reservation_service.calendars:
            if calendar_to_update.collision_with_calendar and \
                    calendar.id in calendar_to_update.collision_with_calendar:
                collision_to_update = calendar_to_update.collision_with_calendar.copy()
                collision_to_update.remove(calendar.id)
                update_exist_calendar = CalendarUpdate(
                    collision_with_calendar=collision_to_update
                )
                await self.update(calendar_to_update.id, update_exist_calendar)

        if hard_remove:
            return await self.crud.remove(calendar_id)

        return await self.crud.soft_remove(calendar_id)

    async def get_all_google_calendar_to_add(
            self, user: User,
            google_calendars: dict
    ) -> list[dict] | None:
        if not user.roles:
            raise PermissionDeniedException()

        new_calendar_candidates = []

        for calendar in google_calendars.get('items', []):
            if calendar.get('accessRole') == 'owner' and not \
                    calendar.get('primary', False):
                if await self.get(calendar.get('id', None)) is None:
                    new_calendar_candidates.append(calendar)

        return new_calendar_candidates

    async def get_by_reservation_type(
            self, reservation_type: str,
            include_removed: bool = False
    ) -> CalendarModel | None:
        return await self.crud.get_by_reservation_type(
            reservation_type, include_removed)

    async def get_mini_services_by_calendar(
            self, calendar_id: str
    ) -> list[str] | None:
        calendar = await self.crud.get(calendar_id)

        if calendar is None:
            return None

        return calendar.mini_services

    async def get_reservation_service_of_this_calendar(
            self, reservation_service_id: UUID
    ) -> ReservationServiceModel | None:
        reservation_service = await self.reservation_service_crud.get(
            reservation_service_id)

        if not reservation_service:
            return None

        return reservation_service

    async def get_by_reservation_service_id(
            self, reservation_service_id: str,
            include_removed: bool = False
    ) -> list[Row[CalendarModel]] | None:
        return await self.crud.get_by_reservation_service_id(reservation_service_id,
                                                             include_removed)
