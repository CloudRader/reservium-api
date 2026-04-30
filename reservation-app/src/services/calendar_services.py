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
)
from core.models import MiniServiceModel
from core.schemas import (
    CalendarCreate,
    CalendarDetail,
    CalendarLite,
    CalendarUpdate,
    MiniServiceLite,
    ReservationServiceDetail,
)
from core.schemas.calendar import CalendarDetailWithCollisions
from core.schemas.google_calendar import CalendarImportResult, GoogleCalendarCalendar
from crud import CRUDCalendar
from fastapi import Depends
from integrations.google import GoogleCalendarService
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
    async def google_calendars_available_for_import(self) -> list[GoogleCalendarCalendar] | None:
        """
        Retrieve a Calendars from Google calendars that are candidates for additions.

        :return: candidate list for additions, None otherwise.
        """

    @abstractmethod
    async def google_subscribe_calendars(
        self,
        calendar_ids: list[str],
    ) -> list[CalendarImportResult]:
        """
        Subscribe the service account to multiple Google Calendars.

        :param calendar_ids: List of Google Calendar IDs to subscribe to.

        :return: List of results describing the outcome for each calendar.
        """

    @abstractmethod
    async def google_subscribe_existing_calendars(self) -> list[CalendarImportResult]:
        """
        Subscribe the service account to all Google Calendars it is already exist in db.

        :return: List of results describing the outcome for each calendar.
        """

    @abstractmethod
    async def google_get_subscribed_calendars(self) -> list[GoogleCalendarCalendar]:
        """
        Retrieve all Google Calendars the service account is subscribed to.

        :return: List of Google Calendar objects.
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
    async def get_mini_services_by_id(self, calendar_id: str) -> list[MiniServiceLite]:
        """
        Retrieve all mini services linked to a given Calendar.

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
        self.google_calendar_service = GoogleCalendarService()

    async def get_with_collisions(
        self,
        id_: str | int,
        include_removed: bool = False,
    ) -> CalendarDetailWithCollisions:
        calendar = await self.crud.get_with_collisions(id_, include_removed)
        if calendar is None:
            raise EntityNotFoundError(self.entity_name, id_)
        return calendar

    async def create(
        self,
        obj_in: CalendarCreate,
    ) -> CalendarDetail:
        if obj_in.id:
            await self.google_calendar_service.user_has_calendar_access(obj_in.id)
        else:
            obj_in.id = (
                await self.google_calendar_service.create_calendar(
                    obj_in.reservation_type,
                )
            ).id

        mini_services_in_calendar = await self._prepare_calendar_mini_services(
            obj_in.reservation_service_id, obj_in.mini_services
        )

        return await self.crud.create_with_mini_services_and_collisions(
            obj_in, mini_services_in_calendar
        )

    async def update(
        self,
        id_: str | int,
        obj_in: CalendarUpdate,
    ) -> CalendarDetail:
        calendar_to_update = await self.crud.get(id_)
        if calendar_to_update is None:
            raise EntityNotFoundError(self.entity_name, id_)

        mini_services_in_calendar = await self._prepare_calendar_mini_services(
            calendar_to_update.reservation_service_id, obj_in.mini_services
        )

        return await self.crud.update_with_mini_services_and_collisions(
            calendar_to_update, obj_in, mini_services_in_calendar
        )

    async def google_calendars_available_for_import(self) -> list[GoogleCalendarCalendar] | None:
        google_calendars = await self.google_calendar_service.get_all_calendars()

        new_calendar_candidates: list[GoogleCalendarCalendar] = []

        for calendar in google_calendars:
            if (
                calendar.access_role == "owner" or calendar.access_role == "writer"
            ) and not calendar.primary:
                try:
                    await self.get(calendar.id)
                    exists = True
                except EntityNotFoundError:
                    exists = False

                if not exists:
                    new_calendar_candidates.append(calendar)

        return new_calendar_candidates

    async def google_subscribe_calendars(
        self,
        calendar_ids: list[str],
    ) -> list[CalendarImportResult]:
        return await self.google_calendar_service.subscribe_calendars(calendar_ids)

    async def google_subscribe_existing_calendars(self) -> list[CalendarImportResult]:
        calendars = await self.get_all()
        calendar_ids = [cal.id for cal in calendars if cal.id is not None]

        return await self.google_calendar_service.subscribe_calendars(calendar_ids)

    async def google_get_subscribed_calendars(self) -> list[GoogleCalendarCalendar]:
        return await self.google_calendar_service.get_all_calendars()

    async def get_by_reservation_type(
        self,
        reservation_type: str,
        include_removed: bool = False,
    ) -> CalendarDetail | None:
        return await self.crud.get_by_reservation_type(
            reservation_type,
            include_removed,
        )

    async def get_mini_services_by_id(self, calendar_id: str) -> list[MiniServiceLite]:
        return (await self.get(calendar_id)).mini_services

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
                message = (
                    f"Mini service {mini_service_id} does not exist or does not belong "
                    f"to this reservation service."
                )
                raise BaseAppError(message)
            mini_services_in_calendar.append(existing_mini_services_by_id[mini_service_id])

        return mini_services_in_calendar
