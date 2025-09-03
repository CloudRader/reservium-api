"""
Define an abstract base class AbstractMiniServiceService.

This class works with Mini Service.
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
from core.models import CalendarModel, EventState, MiniServiceModel
from core.schemas import (
    CalendarDetail,
    MiniServiceDetail,
    ReservationServiceCreate,
    ReservationServiceDetail,
    ReservationServiceUpdate,
    UserLite,
)
from core.schemas.event import EventDetail
from crud import CRUDReservationService
from fastapi import Depends
from services import CrudServiceBase
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractReservationServiceService(
    CrudServiceBase[
        ReservationServiceDetail,
        ReservationServiceDetail,
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
        user: UserLite,
    ) -> ReservationServiceDetail:
        """
        Create a Reservation Service in the database.

        :param reservation_service_create: ReservationServiceCreate SchemaLite for create.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the created Reservation Service.
        """

    @abstractmethod
    async def update_with_permission_checks(
        self,
        id_: str,
        reservation_service_update: ReservationServiceUpdate,
        user: UserLite,
    ) -> ReservationServiceDetail:
        """
        Update a Reservation Service in the database.

        :param id_: The id of the Reservation Service.
        :param reservation_service_update: ReservationServiceUpdate SchemaLite for update.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the updated Reservation Service.
        """

    @abstractmethod
    async def restore_with_permission_checks(
        self,
        id_: str | int,
        user: UserLite,
    ) -> ReservationServiceDetail:
        """
        Retrieve removed object from soft removed.

        :param id_: The id of the object to retrieve from removed.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the updated Reservation Service.
        """

    @abstractmethod
    async def delete_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
        hard_remove: bool = False,
    ) -> ReservationServiceDetail:
        """
        Delete a Reservation Service in the database.

        :param id_: The id of the Reservation Service.
        :param user: the UserSchema for control permissions of the reservation service.
        :param hard_remove: hard remove of the reservation service or not.

        :return: the deleted Reservation Service.
        """

    @abstractmethod
    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        """
        Retrieve a Reservation Service instance by its alias.

        :param alias: The alias of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Services instance.
        """

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        """
        Retrieve a Reservation Service instance by its name.

        :param name: The name of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance.
        """

    @abstractmethod
    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        """
        Retrieve a Reservation Service instance by its room id.

        :param room_id: The room id of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance.
        """

    @abstractmethod
    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationServiceDetail]:
        """
        Retrieve a public Reservation Service instance.

        :param include_removed: Include removed object or not.

        :return: The public Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_all_services_include_all_removed(
        self,
    ) -> list[ReservationServiceDetail]:
        """
        Retrieve Reservation Services instance include soft removed.

        :return: The Reservation Services instance include
        soft removed if found, None otherwise.
        """

    @abstractmethod
    async def get_calendars_by_id(
        self,
        id_: str,
        include_removed: bool = False,
    ) -> list[CalendarDetail]:
        """
        Retrieve all calendars linked to a given Reservation Service.

        :param id_: The id of the Reservation Service.
        :param include_removed: Include removed calendars or not.

        :return: List of CalendarDetail objects linked to the reservation service.
        """

    @abstractmethod
    async def get_mini_services_by_id(
        self,
        id_: str,
        include_removed: bool = False,
    ) -> list[MiniServiceDetail]:
        """
        Retrieve all mini services linked to a given Reservation Service.

        :param id_: The id of the Reservation Service.
        :param include_removed: Include removed calendars or not.

        :return: List of MiniServiceDetail objects linked to the reservation service.
        """

    @abstractmethod
    async def get_events_by_id(
        self,
        id_: str,
        event_state: EventState | None = None,
    ) -> list[EventDetail]:
        """
        Retrieve all events linked to a given Reservation Service.

        :param id_: The id of the Reservation Service.
        :param event_state: event state of the event.

        :return: List of EventWithExtraDetails objects linked to the reservation service.
        """


class ReservationServiceService(AbstractReservationServiceService):
    """Class MiniServiceService represent service that work with Mini Service."""

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(db_session.scoped_session_dependency)],
    ):
        super().__init__(CRUDReservationService(db), Entity.RESERVATION_SERVICE)

    async def create_with_permission_checks(
        self,
        reservation_service_create: ReservationServiceCreate,
        user: UserLite,
    ) -> ReservationServiceDetail:
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
        id_: str,
        reservation_service_update: ReservationServiceUpdate,
        user: UserLite,
    ) -> ReservationServiceDetail:
        if not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to update services.",
            )

        return await self.update(id_, reservation_service_update)

    async def restore_with_permission_checks(
        self,
        id_: str | int,
        user: UserLite,
    ) -> ReservationServiceDetail:
        if not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to retrieve removed services.",
            )

        return await self.restore(id_)

    async def delete_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
        hard_remove: bool = False,
    ) -> ReservationServiceDetail:
        if not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to delete services.",
            )

        if hard_remove:
            return await self.remove(id_)

        return await self.soft_remove(id_)

    async def get_by_alias(
        self,
        alias: str,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        reservation_service = await self.crud.get_by_alias(alias, include_removed)
        if reservation_service is None:
            raise EntityNotFoundError(self.entity_name, alias)
        return reservation_service

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        reservation_service = await self.crud.get_by_name(name, include_removed)
        if reservation_service is None:
            raise EntityNotFoundError(self.entity_name, name)
        return reservation_service

    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> ReservationServiceDetail:
        reservation_service = await self.crud.get_by_room_id(room_id, include_removed)
        if reservation_service is None:
            raise EntityNotFoundError(self.entity_name, room_id)
        return reservation_service

    async def get_public_services(
        self,
        include_removed: bool = False,
    ) -> list[ReservationServiceDetail]:
        return await self.crud.get_public_services(include_removed)

    async def get_all_services_include_all_removed(
        self,
    ) -> list[ReservationServiceDetail]:
        reservation_services: list[ReservationServiceDetail] = await self.crud.get_all(
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

    async def get_calendars_by_id(
        self,
        id_: str,
        include_removed: bool = False,
    ) -> list[CalendarDetail]:
        reservation_service = await self.get(id_, include_removed=True)

        return await self.crud.get_related_entities_by_reservation_service_id(
            CalendarModel, reservation_service.id, include_removed=include_removed
        )

    async def get_mini_services_by_id(
        self,
        id_: str,
        include_removed: bool = False,
    ) -> list[MiniServiceDetail]:
        reservation_service = await self.get(id_, include_removed=True)

        return await self.crud.get_related_entities_by_reservation_service_id(
            MiniServiceModel, reservation_service.id, include_removed=include_removed
        )

    async def get_events_by_id(
        self,
        id_: str,
        event_state: EventState | None = None,
    ) -> list[EventDetail]:
        reservation_service = await self.get(id_, include_removed=True)

        return await self.crud.get_events_by_reservation_service_id(
            reservation_service.id,
            event_state,
        )
