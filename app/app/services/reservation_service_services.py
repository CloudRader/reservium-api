"""
This module defines an abstract base class AbstractReservationServiceService
that work with Reservation Service
"""
from typing import Annotated
from abc import ABC, abstractmethod
from uuid import UUID

from db import db_session
from fastapi import Depends
from crud import CRUDReservationService, CRUDCalendar, CRUDMiniService
from api import BaseAppException, PermissionDeniedException
from services import CrudServiceBase
from models import ReservationServiceModel
from schemas import ReservationServiceCreate, ReservationServiceUpdate, User
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractReservationServiceService(CrudServiceBase[
                                            ReservationServiceModel,
                                            CRUDReservationService,
                                            ReservationServiceCreate,
                                            ReservationServiceUpdate,
                                        ], ABC):
    """
    This abstract class defines the interface for a reservation service ser
    that provides CRUD operations for a specific ReservationServiceModel.
    """

    @abstractmethod
    async def create_reservation_service(self, reservation_service_create: ReservationServiceCreate,
                                         user: User) -> ReservationServiceModel | None:
        """
        Create a Reservation Service in the database.

        :param reservation_service_create: ReservationServiceCreate Schema for create.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the created Reservation Service.
        """

    @abstractmethod
    async def update_reservation_service(self, uuid: UUID,
                                         reservation_service_update: ReservationServiceUpdate,
                                         user: User) -> ReservationServiceModel | None:
        """
        Update a Reservation Service in the database.

        :param uuid: The uuid of the Reservation Service.
        :param reservation_service_update: ReservationServiceUpdate Schema for update.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the updated Reservation Service.
        """

    @abstractmethod
    async def retrieve_removed_object(self, uuid: UUID | str | int | None,
                                      user: User
                                      ) -> ReservationServiceModel | None:
        """
        Retrieve removed object from soft removed.

        :param uuid: The ID of the object to retrieve from removed.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the updated Reservation Service.
        """

    @abstractmethod
    async def delete_reservation_service(self, uuid: UUID,
                                         user: User,
                                         hard_remove: bool = False
                                         ) -> ReservationServiceModel | None:
        """
        Delete a Reservation Service in the database.

        :param uuid: The uuid of the Reservation Service.
        :param user: the UserSchema for control permissions of the reservation service.
        :param hard_remove: hard remove of the reservation service or not.

        :return: the deleted Reservation Service.
        """

    @abstractmethod
    async def get_by_alias(self, alias: str,
                           include_removed: bool = False) -> ReservationServiceModel | None:
        """
        Retrieves a Reservation Service instance by its alias.

        :param alias: The alias of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Services instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_name(self, name: str,
                          include_removed: bool = False) -> ReservationServiceModel | None:
        """
        Retrieves a Reservation Service instance by its name.

        :param name: The name of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_room_id(
            self, room_id: int,
            include_removed: bool = False
    ) -> ReservationServiceModel | None:
        """
        Retrieves a Reservation Service instance by its room id.

        :param room_id: The room id of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_public_services(
            self, include_removed: bool = False
    ) -> list[Row[ReservationServiceModel]] | None:
        """
        Retrieves a public Reservation Service instance.

        :param include_removed: Include removed object or not.

        :return: The public Reservation Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_all_services_include_all_removed(
            self,
    ) -> list[ReservationServiceModel]:
        """
        Retrieves Reservation Services instance include soft removed
        (soft deleted calendars and mini services too).

        :return: The Reservation Services instance include
        soft removed if found, None otherwise.
        """


class ReservationServiceService(AbstractReservationServiceService):
    """
    Class MiniServiceService represent service that work with Mini Service
    """

    def __init__(self, db: Annotated[
        AsyncSession, Depends(db_session.scoped_session_dependency)]):
        super().__init__(CRUDReservationService(db))
        self.calendar_crud = CRUDCalendar(db)
        self.mini_service_crud = CRUDMiniService(db)

    async def create_reservation_service(self, reservation_service_create: ReservationServiceCreate,
                                         user: User) -> ReservationServiceModel | None:
        if await self.crud.get_by_name(reservation_service_create.name, True):
            raise BaseAppException("A reservation service with this name already exist.")
        if await self.crud.get_by_alias(reservation_service_create.alias, True):
            raise BaseAppException("A reservation service with this alias already exist.")

        if not user.section_head:
            raise PermissionDeniedException("You must be the head of PS to create services.")

        return await self.crud.create(reservation_service_create)

    async def update_reservation_service(self, uuid: UUID,
                                         reservation_service_update: ReservationServiceUpdate,
                                         user: User) -> ReservationServiceModel | None:
        if not user.section_head:
            raise PermissionDeniedException("You must be the head of PS to update services.")

        return await self.update(uuid, reservation_service_update)

    async def retrieve_removed_object(self, uuid: UUID | str | int | None,
                                      user: User
                                      ) -> ReservationServiceModel | None:
        if not user.section_head:
            raise PermissionDeniedException(
                "You must be the head of PS to retrieve removed services.")

        return await self.crud.retrieve_removed_object(uuid)

    async def delete_reservation_service(
            self, uuid: UUID,
            user: User,
            hard_remove: bool = False
    ) -> ReservationServiceModel | None:
        if not user.section_head:
            raise PermissionDeniedException("You must be the head of PS to delete services.")

        if hard_remove:
            return await self.crud.remove(uuid)

        return await self.crud.soft_remove(uuid)

    async def get_by_alias(self, alias: str,
                           include_removed: bool = False) -> ReservationServiceModel | None:
        return await self.crud.get_by_alias(alias, include_removed)

    async def get_by_name(self, name: str,
                          include_removed: bool = False) -> ReservationServiceModel | None:
        return await self.crud.get_by_name(name, include_removed)

    async def get_by_room_id(
            self, room_id: int,
            include_removed: bool = False
    ) -> ReservationServiceModel | None:
        return await self.crud.get_by_room_id(room_id, include_removed)

    async def get_public_services(
            self, include_removed: bool = False
    ) -> list[Row[ReservationServiceModel]] | None:
        services = await self.crud.get_public_services(include_removed)
        if len(services) == 0:
            return []
        return services

    async def get_all_services_include_all_removed(
            self,
    ) -> list[ReservationServiceModel]:
        reservation_services: list[ReservationServiceModel] = await self.crud.get_all(True)

        for reservation_service in reservation_services:
            calendars = await self.calendar_crud.get_by_reservation_service_id(
                reservation_service.id, include_removed=True
            )

            mini_services = await self.mini_service_crud.get_by_reservation_service_id(
                reservation_service.id, include_removed=True
            )

            reservation_service.calendars = calendars
            reservation_service.mini_services = mini_services

        return reservation_services
