"""
Define an abstract base class AbstractMiniServiceService.

This class works with Mini Service.
"""

from abc import ABC, abstractmethod
from typing import Annotated
from uuid import UUID

from api import BaseAppError, Entity, EntityNotFoundError, PermissionDeniedError
from core import db_session
from core.models import CalendarModel, EventState, MiniServiceModel, ReservationServiceModel
from core.schemas import (
    EventWithExtraDetails,
    ReservationService,
    ReservationServiceCreate,
    ReservationServiceUpdate,
    User,
)
from crud import CRUDCalendar, CRUDMiniService, CRUDReservationService
from fastapi import Depends
from services import CrudServiceBase
from services.event_services import EventService
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractReservationServiceService(
    CrudServiceBase[
        ReservationServiceModel,
        CRUDReservationService,
        ReservationServiceCreate,
        ReservationServiceUpdate,
    ],
    ABC,
):
    """
    Abstract class defines the interface for a reservation service ser.

    Provides CRUD operations for a specific ReservationServiceModel.
    """

    @abstractmethod
    async def create_with_permission_checks(
        self,
        reservation_service_create: ReservationServiceCreate,
        user: User,
    ) -> ReservationServiceModel | None:
        """
        Create a Reservation Service in the database.

        :param reservation_service_create: ReservationServiceCreate Schema for create.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the created Reservation Service.
        """

    @abstractmethod
    async def update_with_permission_checks(
        self,
        uuid: UUID,
        reservation_service_update: ReservationServiceUpdate,
        user: User,
    ) -> ReservationServiceModel | None:
        """
        Update a Reservation Service in the database.

        :param uuid: The uuid of the Reservation Service.
        :param reservation_service_update: ReservationServiceUpdate Schema for update.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the updated Reservation Service.
        """

    @abstractmethod
    async def restore_with_permission_checks(
        self,
        uuid: UUID | str | int | None,
        user: User,
    ) -> ReservationServiceModel | None:
        """
        Retrieve removed object from soft removed.

        :param uuid: The ID of the object to retrieve from removed.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the updated Reservation Service.
        """

    @abstractmethod
    async def delete_with_permission_checks(
        self,
        uuid: UUID,
        user: User,
        hard_remove: bool = False,
    ) -> ReservationServiceModel | None:
        """
        Delete a Reservation Service in the database.

        :param uuid: The uuid of the Reservation Service.
        :param user: the UserSchema for control permissions of the reservation service.
        :param hard_remove: hard remove of the reservation service or not.

        :return: the deleted Reservation Service.
        """

    @abstractmethod
    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        """
        Retrieve a Reservation Service instance by its alias.

        :param alias: The alias of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Services instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        """
        Retrieve a Reservation Service instance by its name.

        :param name: The name of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        """
        Retrieve a Reservation Service instance by its room id.

        :param room_id: The room id of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[Row[ReservationServiceModel]] | None:
        """
        Retrieve a public Reservation Service instance.

        :param include_removed: Include removed object or not.

        :return: The public Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_all_services_include_all_removed(
        self,
    ) -> list[ReservationServiceModel]:
        """
        Retrieve Reservation Services instance include soft removed.

        :return: The Reservation Services instance include
        soft removed if found, None otherwise.
        """

    @abstractmethod
    async def get_calendars_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> list[CalendarModel]:
        """
        Retrieve all calendars linked to a given Reservation Service.

        :param alias: The alias of the Reservation Service.
        :param include_removed: Include removed calendars or not.

        :return: List of Calendar objects linked to the reservation service.
        """

    @abstractmethod
    async def get_mini_services_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> list[MiniServiceModel]:
        """
        Retrieve all mini services linked to a given Reservation Service.

        :param alias: The alias of the Reservation Service.
        :param include_removed: Include removed calendars or not.

        :return: List of MiniService objects linked to the reservation service.
        """

    @abstractmethod
    async def get_events_by_alias(
        self,
        alias: str,
        event_state: EventState | None = None,
    ) -> list[EventWithExtraDetails]:
        """
        Retrieve all events linked to a given Reservation Service.

        :param alias: The alias of the Reservation Service.
        :param event_state: event state of the event.

        :return: List of EventWithExtraDetails objects linked to the reservation service.
        """


class ReservationServiceService(AbstractReservationServiceService):
    """Class MiniServiceService represent service that work with Mini Service."""

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(db_session.scoped_session_dependency)],
    ):
        super().__init__(CRUDReservationService(db))
        self.event_service = EventService(db)
        self.calendar_crud = CRUDCalendar(db)
        self.mini_service_crud = CRUDMiniService(db)

    async def create_with_permission_checks(
        self,
        reservation_service_create: ReservationServiceCreate,
        user: User,
    ) -> ReservationServiceModel | None:
        if await self.crud.get_by_name(reservation_service_create.name, True):
            raise BaseAppError("A reservation service with this name already exist.")
        if await self.crud.get_by_alias(reservation_service_create.alias, True):
            raise BaseAppError("A reservation service with this alias already exist.")

        if not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to create services.",
            )

        return await self.crud.create(reservation_service_create)

    async def update_with_permission_checks(
        self,
        uuid: UUID,
        reservation_service_update: ReservationServiceUpdate,
        user: User,
    ) -> ReservationServiceModel | None:
        if not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to update services.",
            )

        return await self.update(uuid, reservation_service_update)

    async def restore_with_permission_checks(
        self,
        uuid: UUID | str | int | None,
        user: User,
    ) -> ReservationServiceModel | None:
        if not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to retrieve removed services.",
            )

        return await self.crud.retrieve_removed_object(uuid)

    async def delete_with_permission_checks(
        self,
        uuid: UUID,
        user: User,
        hard_remove: bool = False,
    ) -> ReservationServiceModel | None:
        if not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to delete services.",
            )

        if hard_remove:
            return await self.crud.remove(uuid)

        return await self.crud.soft_remove(uuid)

    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        return await self.crud.get_by_alias(alias, include_removed)

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        return await self.crud.get_by_name(name, include_removed)

    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> ReservationServiceModel | None:
        return await self.crud.get_by_room_id(room_id, include_removed)

    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[Row[ReservationServiceModel]] | None:
        services = await self.crud.get_public_services(include_removed)
        if len(services) == 0:
            return []
        return services

    async def get_all_services_include_all_removed(
        self,
    ) -> list[ReservationServiceModel]:
        reservation_services: list[ReservationServiceModel] = await self.crud.get_all(
            True,
        )

        for reservation_service in reservation_services:
            calendars = await self.crud.get_related_entities_by_reservation_service_id(
                CalendarModel,
                reservation_service.id,
                include_removed=True,
            )

            mini_services = await self.crud.get_related_entities_by_reservation_service_id(
                MiniServiceModel,
                reservation_service.id,
                include_removed=True,
            )

            reservation_service.calendars = calendars
            reservation_service.mini_services = mini_services

        return reservation_services

    async def get_calendars_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> list[CalendarModel]:
        reservation_service = await self.__get_reservation_service_if_exist(alias)

        return await self.crud.get_related_entities_by_reservation_service_id(
            CalendarModel, reservation_service.id, include_removed=include_removed
        )

    async def get_mini_services_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> list[MiniServiceModel]:
        reservation_service = await self.__get_reservation_service_if_exist(alias)

        return await self.crud.get_related_entities_by_reservation_service_id(
            MiniServiceModel, reservation_service.id, include_removed=include_removed
        )

    async def __get_reservation_service_if_exist(self, alias: str) -> ReservationService:
        """
        Retrieve a Reservation Service by its ID or raise an error if not found.

        :param alias: alias of the Reservation Service to retrieve.

        :return: The Reservation Service instance if found.
        """
        reservation_service = await self.get_by_alias(alias)
        if reservation_service is None:
            raise EntityNotFoundError(Entity.RESERVATION_SERVICE, alias)
        return reservation_service

    async def get_events_by_alias(
        self,
        alias: str,
        event_state: EventState | None = None,
    ) -> list[EventWithExtraDetails]:
        reservation_service = await self.crud.get_by_alias(
            alias,
        )

        if not reservation_service:
            raise BaseAppError(
                "A reservation service with this alias isn't exist.",
                status_code=404,
            )

        events = await self.crud.get_events_by_reservation_service_id(
            reservation_service.id,
            event_state,
        )

        return await self.event_service.add_extra_details_to_event(events)
