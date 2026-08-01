"""
Define an abstract base class AbstractCalendarService.

This class works with Calendar.
"""

import dataclasses
from abc import ABC, abstractmethod
from uuid import UUID

from application.mappers import CalendarMapper
from application.ports.providers.calendar import CalendarProvider
from application.ports.repositories import CalendarRepository, MiniServiceRepository
from application.schemas import (
    CalendarCreate,
    CalendarSchema,
    CalendarUpdate,
)
from application.schemas.calendar import CalendarWithCollisions
from application.services import BaseService
from core.bootstrap.exceptions import (
    BaseAppError,
    Entity,
    EntityNotFoundError,
)
from domain.entities import Calendar, MiniService
from domain.value_objects import Rules as DomainRules
from infrastructure.calendar.google import (
    CalendarImportResult,
    GoogleCalendarCalendar,
)


class AbstractCalendarService(
    BaseService[
        CalendarSchema,
        CalendarRepository,
        Calendar,
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
        id_: UUID,
        include_removed: bool = False,
    ) -> CalendarWithCollisions:
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
    ) -> CalendarSchema | None:
        """
        Retrieve a Calendar instance by its reservation_type.

        :param reservation_type: The reservation type of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_provider_id(
        self,
        provider_id: str,
        include_removed: bool = False,
    ) -> CalendarSchema | None:
        """
        Retrieve a Calendar instance by its provider_id.

        :param provider_id: The provider_id of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        include_removed: bool = False,
    ) -> list[CalendarSchema]:
        """
        Retrieve calendars by reservation service ID.

        :param reservation_service_id: The ID of the reservation service.
        :param include_removed: Optional flag to include removed calendars.
        :return: List of CalendarDetail schemas linked to the reservation service.
        """


class CalendarService(AbstractCalendarService):
    """Class CalendarService represent service that work with Calendar."""

    def __init__(
        self,
        calendar_repository: CalendarRepository,
        mini_service_repository: MiniServiceRepository,
        calendar_provider: CalendarProvider,
        mapper: CalendarMapper,
    ):
        super().__init__(
            calendar_repository,
            Entity.CALENDAR,
            CalendarSchema,
            mapper,
        )
        self.mini_service_repo = mini_service_repository
        self.google_calendar_service = calendar_provider

    async def get_with_collisions(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> CalendarWithCollisions:
        calendar = await self.repo.get_with_collisions(id_, include_removed)
        if calendar is None:
            raise EntityNotFoundError(self.entity_name, id_)
        return self.mapper.to_entity(calendar)

    async def create(
        self,
        obj_in: CalendarCreate,
    ) -> CalendarSchema:
        if obj_in.provider_id:
            await self.google_calendar_service.user_has_calendar_access(obj_in.provider_id)
        else:
            obj_in.provider_id = (
                await self.google_calendar_service.create_calendar(obj_in.reservation_type)
            ).id

        mini_services_in_calendar = await self._prepare_calendar_mini_services(
            obj_in.reservation_service_id, obj_in.mini_services
        )

        calendar_entity = CalendarMapper().to_entity(obj_in)

        created = await self.repo.create_with_mini_services_and_collisions(
            calendar_entity, mini_services_in_calendar, obj_in.collision_ids
        )
        return self.mapper.to_schema(created)

    async def update(
        self,
        id_: UUID,
        obj_in: CalendarUpdate,
    ) -> CalendarSchema:
        calendar_to_update = await self.repo.get(id_)
        if calendar_to_update is None:
            raise EntityNotFoundError(self.entity_name, id_)

        mini_services_in_calendar = await self._prepare_calendar_mini_services(
            calendar_to_update.reservation_service_id, obj_in.mini_services
        )

        update_data = obj_in.model_dump(exclude_unset=True)
        if "mini_services" in update_data:
            update_data["mini_service_ids"] = update_data.pop("mini_services")
        if update_data.get("club_member_rules"):
            update_data["club_member_rules"] = DomainRules(**update_data["club_member_rules"])
        if update_data.get("active_member_rules"):
            update_data["active_member_rules"] = DomainRules(**update_data["active_member_rules"])
        if update_data.get("manager_rules"):
            update_data["manager_rules"] = DomainRules(**update_data["manager_rules"])

        updated_calendar = dataclasses.replace(calendar_to_update, **update_data)

        updated = await self.repo.update_with_mini_services_and_collisions(
            updated_calendar, mini_services_in_calendar, obj_in.collision_ids
        )
        return self.mapper.to_schema(updated)

    async def google_calendars_available_for_import(self) -> list[GoogleCalendarCalendar] | None:
        google_calendars = await self.google_calendar_service.get_all_calendars()

        new_calendar_candidates: list[GoogleCalendarCalendar] = []

        for calendar in google_calendars:
            if (
                calendar.access_role == "owner" or calendar.access_role == "writer"
            ) and not calendar.primary:
                calendar_exist = await self.get_by_provider_id(calendar.id)

                if not calendar_exist:
                    new_calendar_candidates.append(calendar)

        return new_calendar_candidates

    async def google_subscribe_calendars(
        self,
        calendar_ids: list[str],
    ) -> list[CalendarImportResult]:
        return await self.google_calendar_service.subscribe_calendars(calendar_ids)

    async def google_subscribe_existing_calendars(self) -> list[CalendarImportResult]:
        calendars = await self.get_all()
        calendar_ids = [cal.provider_id for cal in calendars if cal.provider_id is not None]

        return await self.google_calendar_service.subscribe_calendars(calendar_ids)

    async def google_get_subscribed_calendars(self) -> list[GoogleCalendarCalendar]:
        return await self.google_calendar_service.get_all_calendars()

    async def get_by_reservation_type(
        self,
        reservation_type: str,
        include_removed: bool = False,
    ) -> CalendarSchema | None:
        calendar = await self.repo.get_by_reservation_type(
            reservation_type,
            include_removed,
        )
        return self.mapper.to_schema(calendar)

    async def get_by_provider_id(
        self,
        provider_id: str,
        include_removed: bool = False,
    ) -> CalendarSchema | None:
        calendar = await self.repo.get_by_provider_id(
            provider_id,
            include_removed,
        )
        return self.mapper.to_schema(calendar)

    async def get_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
        include_removed: bool = False,
    ) -> list[CalendarSchema]:
        calendars = await self.repo.get_by_reservation_service_id(
            reservation_service_id, include_removed
        )
        return [self.mapper.to_schema(calendar) for calendar in calendars]

    async def _prepare_calendar_mini_services(
        self,
        reservation_service_id: UUID,
        mini_services_ids: list[UUID],
    ) -> list[MiniService]:
        """
        Validate mini service IDs.

        Prepare the corresponding MiniService objects for association with a calendar.
        Ensures that all provided mini service IDs exist for the given reservation service.
        """
        mini_services_in_calendar = []
        mini_services = await self.mini_service_repo.get_by_reservation_service_id(
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
