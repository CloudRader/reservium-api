"""
Define an abstract base class AbstractCalendarService.

This class works with Calendar.
"""

from abc import ABC, abstractmethod
from typing import Annotated

from core import db_session
from core.application.exceptions import (
    BaseAppError,
    Entity,
    EntityNotFoundError,
    PermissionDeniedError,
)
from core.models import MiniServiceModel
from core.schemas import (
    CalendarCreate,
    CalendarDetail,
    CalendarLite,
    CalendarUpdate,
    ReservationServiceDetail,
    UserLite,
)
from core.schemas.calendar import CalendarDetailWithCollisions
from core.schemas.google_calendar import GoogleCalendarCalendar
from crud import CRUDCalendar
from fastapi import Depends
from services import CrudServiceBase
from services.mini_service_services import MiniServiceService
from services.reservation_service_services import ReservationServiceService
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractCalendarService(
    CrudServiceBase[
        CalendarLite,
        CalendarDetail,
        CRUDCalendar,
        CalendarCreate,
        CalendarUpdate,
    ],
    ABC,
):
    """
    Abstract class defines the interface for a calendar service.

    Provides CRUD operations for a specific CalendarModel.
    """

    @abstractmethod
    async def get_with_collisions(
        self,
        id_: str | int,
        include_removed: bool = False,
    ) -> CalendarDetailWithCollisions:
        """
        Retrieve a single record by its id_ with collisions.

        If include_removed is True retrieve a single record
        including marked as deleted.
        """

    @abstractmethod
    async def create_with_permission_checks(
        self,
        calendar_create: CalendarCreate,
        user: UserLite,
    ) -> CalendarDetail:
        """
        Create a Calendar in the database.

        :param calendar_create: CalendarCreate SchemaLite for create.
        :param user: the UserSchema for control permissions of the calendar.

        :return: the created Calendar.
        """

    @abstractmethod
    async def update_with_permission_checks(
        self,
        id_: str,
        calendar_update: CalendarUpdate,
        user: UserLite,
    ) -> CalendarDetail:
        """
        Update a Calendar in the database.

        :param id_: The id of the Calendar.
        :param calendar_update: CalendarUpdate SchemaLite for update.
        :param user: the UserSchema for control permissions of the calendar.

        :return: the updated Calendar.
        """

    @abstractmethod
    async def restore_with_permission_checks(
        self,
        id_: str | int | None,
        user: UserLite,
    ) -> CalendarDetail:
        """
        Retrieve removed calendar from soft removed.

        :param id_: The ID of the calendar to retrieve from removed.
        :param user: the UserSchema for control permissions of the calendar.

        :return: the updated CalendarDetail.
        """

    @abstractmethod
    async def delete_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
        hard_remove: bool = False,
    ) -> CalendarDetail:
        """
        Delete a Calendar in the database.

        :param id_: The id of the Calendar.
        :param user: the UserSchema for control permissions of the calendar.
        :param hard_remove: hard remove of the calendar or not.

        :return: the deleted Calendar.
        """

    @abstractmethod
    async def google_calendars_available_for_import(
        self,
        user: UserLite,
        google_calendars: list[GoogleCalendarCalendar],
    ) -> list[GoogleCalendarCalendar] | None:
        """
        Retrieve a Calendars from Google calendars that are candidates for additions.

        :param user: the UserSchema for control permissions of the calendar.
        :param google_calendars: calendars from Google Calendars.

        :return: candidate list for additions, None otherwise.
        """

    @abstractmethod
    async def get_by_reservation_type(
        self,
        reservation_type: str,
        include_removed: bool = False,
    ) -> CalendarDetail | None:
        """
        Retrieve a Calendar instance by its reservation_type.

        :param reservation_type: The reservation type of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    async def get_mini_services_by_calendar(self, calendar_id: str) -> list[str]:
        """
        Retrieve a list mini services instance by its calendar id.

        :param calendar_id: The id of the Calendar.

        :return: The list of mini services.
        """

    @abstractmethod
    async def get_reservation_service(
        self,
        id_: str,
    ) -> ReservationServiceDetail:
        """
        Retrieve the reservation service of this calendar by reservation service id.

        :param id_: The id of the calendar.

        :return: Reservation Service of this calendar if found.
        """


class CalendarService(AbstractCalendarService):
    """Class CalendarService represent service that work with Calendar."""

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(db_session.scoped_session_dependency)],
    ):
        super().__init__(CRUDCalendar(db), Entity.CALENDAR)
        self.reservation_service_service = ReservationServiceService(db)
        self.mini_service_service = MiniServiceService(db)
        self.entity_name = Entity.CALENDAR

    async def get_with_collisions(
        self,
        id_: str | int,
        include_removed: bool = False,
    ) -> CalendarDetailWithCollisions:
        calendar = await self.crud.get_with_collisions(id_, include_removed)
        if calendar is None:
            raise EntityNotFoundError(self.entity_name, id_)
        return calendar

    async def create_with_permission_checks(
        self,
        calendar_create: CalendarCreate,
        user: UserLite,
    ) -> CalendarDetail:
        reservation_service = await self.reservation_service_service.get(
            calendar_create.reservation_service_id,
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to create calendars.",
            )

        mini_services_in_calendar = await self._prepare_calendar_mini_services(
            calendar_create.reservation_service_id, calendar_create.mini_services
        )

        return await self.crud.create_with_mini_services_and_collisions(
            calendar_create, mini_services_in_calendar
        )

    async def update_with_permission_checks(
        self,
        id_: str,
        calendar_update: CalendarUpdate,
        user: UserLite,
    ) -> CalendarDetail:
        calendar_to_update = await self.get(id_)

        reservation_service = await self.reservation_service_service.get(
            calendar_to_update.reservation_service_id
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to create calendars.",
            )

        mini_services_in_calendar = await self._prepare_calendar_mini_services(
            calendar_to_update.reservation_service_id, calendar_update.mini_services
        )

        return await self.crud.update_with_mini_services_and_collisions(
            calendar_to_update, calendar_update, mini_services_in_calendar
        )

    async def restore_with_permission_checks(
        self,
        id_: str | int | None,
        user: UserLite,
    ) -> CalendarDetail:
        calendar = await self.get(id_, True)

        reservation_service = await self.reservation_service_service.get(
            str(calendar.reservation_service_id),
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to create calendars.",
            )

        return await self.restore(id_)

    async def delete_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
        hard_remove: bool = False,
    ) -> CalendarDetail:
        calendar = await self.get(id_, True)

        if hard_remove and not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to totally delete calendars.",
            )

        reservation_service = await self.reservation_service_service.get(
            calendar.reservation_service_id,
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to create calendars.",
            )

        if hard_remove:
            return await self.remove(id_)

        return await self.soft_remove(id_)

    async def google_calendars_available_for_import(
        self,
        user: UserLite,
        google_calendars: list[GoogleCalendarCalendar],
    ) -> list[GoogleCalendarCalendar] | None:
        if not user.roles:
            raise PermissionDeniedError()

        new_calendar_candidates: list[GoogleCalendarCalendar] = []

        for calendar in google_calendars:
            if calendar.access_role == "owner" and not calendar.primary:
                try:
                    await self.get(calendar.id)
                    exists = True
                except EntityNotFoundError:
                    exists = False

                if not exists:
                    new_calendar_candidates.append(calendar)

        return new_calendar_candidates

    async def get_by_reservation_type(
        self,
        reservation_type: str,
        include_removed: bool = False,
    ) -> CalendarDetail | None:
        return await self.crud.get_by_reservation_type(
            reservation_type,
            include_removed,
        )

    async def get_mini_services_by_calendar(self, calendar_id: str) -> list[str]:
        calendar = await self.get(calendar_id)

        mini_services_name = []
        for mini_service in calendar.mini_services:
            mini_services_name.append(mini_service.name)

        return mini_services_name

    async def get_reservation_service(
        self,
        id_: str,
    ) -> ReservationServiceDetail:
        calendar = await self.get(id_, True)
        return await self.reservation_service_service.get(calendar.reservation_service_id, True)

    async def _prepare_calendar_mini_services(
        self,
        reservation_service_id: str,
        mini_services_ids: list[str],
    ) -> list[MiniServiceModel]:
        """
        Validate mini service IDs.

        Prepare the corresponding MiniService objects for association with a calendar.
        Ensures that all provided mini service IDs exist for the given reservation service.
        """
        mini_services_in_calendar = []
        mini_services = await self.reservation_service_service.get_mini_services_by_id(
            reservation_service_id
        )
        existing_mini_services_by_id = {ms.id: ms for ms in mini_services}

        for mini_service_id in mini_services_ids:
            if mini_service_id not in existing_mini_services_by_id:
                raise BaseAppError(
                    f"Mini service {mini_service_id} does not exist or does not belong "
                    f"to this reservation service.",
                )
            mini_services_in_calendar.append(existing_mini_services_by_id[mini_service_id])

        return mini_services_in_calendar
