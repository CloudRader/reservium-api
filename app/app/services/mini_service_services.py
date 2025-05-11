"""
This module defines an abstract base class AbstractMiniServiceService that work with Mini Service
"""
from typing import Annotated
from abc import ABC, abstractmethod
from uuid import UUID

from db import db_session
from fastapi import Depends
from api import BaseAppException, PermissionDeniedException
from crud import CRUDMiniService, CRUDCalendar, CRUDReservationService
from services import CrudServiceBase
from models import MiniServiceModel
from schemas import MiniServiceCreate, MiniServiceUpdate, CalendarUpdate, User
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractMiniServiceService(CrudServiceBase[
                                     MiniServiceModel,
                                     CRUDMiniService,
                                     MiniServiceCreate,
                                     MiniServiceUpdate,
                                 ], ABC):
    """
    This abstract class defines the interface for a mini service ser
    that provides CRUD operations for a specific MiniServiceModel.
    """

    @abstractmethod
    async def create_mini_service(self, mini_service_create: MiniServiceCreate,
                                  user: User) -> MiniServiceModel | None:
        """
        Create a Mini Service in the database.

        :param mini_service_create: MiniServiceCreate Schema for create.
        :param user: the UserSchema for control permissions of the mini service.

        :return: the created Mini Service.
        """

    @abstractmethod
    async def update_mini_service(self, uuid: UUID,
                                  mini_service_update: MiniServiceUpdate,
                                  user: User) -> MiniServiceModel | None:
        """
        Update a Mini Service in the database.

        :param uuid: The uuid of the Mini Service.
        :param mini_service_update: MiniServiceUpdate Schema for update.
        :param user: the UserSchema for control permissions of the mini service.

        :return: the updated Mini Service.
        """

    @abstractmethod
    async def retrieve_removed_object(
            self, uuid: UUID | str | int | None,
            user: User
    ) -> MiniServiceModel | None:
        """
        Retrieve removed mini service from soft removed.

        :param uuid: The ID of the mini service to retrieve from removed.
        :param user: the UserSchema for control permissions of the mini service.

        :return: the updated Mini Service.
        """

    @abstractmethod
    async def delete_mini_service(
            self, uuid: UUID,
            user: User,
            hard_remove: bool = False
    ) -> MiniServiceModel | None:
        """
        Delete a Mini Service in the database.

        :param uuid: The uuid of the Mini Service.
        :param user: the UserSchema for control permissions of the mini service.
        :param hard_remove: hard remove of the reservation service or not.

        :return: the deleted Mini Service.
        """

    @abstractmethod
    async def get_by_name(self, name: str,
                          include_removed: bool = False) -> MiniServiceModel | None:
        """
        Retrieves a Mini Service instance by its name.

        :param name: The name of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_room_id(
            self, room_id: int,
            include_removed: bool = False
    ) -> MiniServiceModel | None:
        """
        Retrieves a Mini Service instance by its room id.

        :param room_id: The room id of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_reservation_service_id(
            self,
            reservation_service_id: UUID,
            include_removed: bool = False
    ) -> list[Row[MiniServiceModel]] | None:
        """
        Retrieves a Mini Service instance by reservation service id.

        :param reservation_service_id: reservation service id of the mini services.
        :param include_removed: Include removed object or not.

        :return: Mini Services with reservation service id equal
        to reservation service id or None if no such mini services exists.
        """


class MiniServiceService(AbstractMiniServiceService):
    """
    Class MiniServiceService represent service that work with Mini Service
    """

    def __init__(self, db: Annotated[
        AsyncSession, Depends(db_session.scoped_session_dependency)]):
        self.calendar_crud = CRUDCalendar(db)
        self.reservation_service_crud = CRUDReservationService(db)
        super().__init__(CRUDMiniService(db))

    async def create_mini_service(self, mini_service_create: MiniServiceCreate,
                                  user: User) -> MiniServiceModel | None:
        if await self.crud.get_by_name(mini_service_create.name, True):
            raise BaseAppException("A reservation service with this name already exist.")

        reservation_service = await self.reservation_service_crud.get(
            mini_service_create.reservation_service_id
        )

        if reservation_service is None:
            raise BaseAppException("A reservation service of mini service isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to create mini services."
            )

        return await self.crud.create(mini_service_create)

    async def update_mini_service(self, uuid: UUID,
                                  mini_service_update: MiniServiceUpdate,
                                  user: User) -> MiniServiceModel | None:
        mini_service_to_update = await self.get(uuid)

        if mini_service_to_update is None:
            return None

        reservation_service = await self.reservation_service_crud.get(
            mini_service_to_update.reservation_service_id
        )

        if reservation_service is None:
            raise BaseAppException("A reservation service of mini service isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to update mini services."
            )

        return await self.update(uuid, mini_service_update)

    async def retrieve_removed_object(self, uuid: UUID | str | int | None,
                                      user: User
                                      ) -> MiniServiceModel | None:
        mini_service = await self.crud.get(uuid, True)

        if mini_service.deleted_at is None:
            raise BaseAppException("A mini service was not soft deleted.")

        reservation_service = await self.reservation_service_crud.get(
            str(mini_service.reservation_service_id)
        )

        if reservation_service is None:
            raise BaseAppException("A reservation service of mini service isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to retrieve mini services."
            )

        return await self.crud.retrieve_removed_object(uuid)

    async def delete_mini_service(self, uuid: UUID,
                                  user: User,
                                  hard_remove: bool = False
                                  ) -> MiniServiceModel | None:
        mini_service = await self.crud.get(uuid, True)

        if mini_service is None:
            return None

        if hard_remove and not user.section_head:
            raise PermissionDeniedException(
                "You must be the head of PS to totally delete mini services.")

        reservation_service = await self.reservation_service_crud.get(
            mini_service.reservation_service_id
        )

        if reservation_service is None:
            raise BaseAppException("A reservation service of mini service isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedException(
                f"You must be the {reservation_service.name} manager to delete mini services."
            )

        for calendar in reservation_service.calendars:
            if mini_service.name in calendar.mini_services:
                list_of_mini_services = calendar.mini_services.copy()
                list_of_mini_services.remove(mini_service.name)
                update_exist_calendar = CalendarUpdate(
                    mini_services=list_of_mini_services
                )
                await self.calendar_crud.update(db_obj=calendar, obj_in=update_exist_calendar)

        if hard_remove:
            return await self.crud.remove(uuid)

        return await self.crud.soft_remove(uuid)

    async def get_by_name(self, name: str,
                          include_removed: bool = False) -> MiniServiceModel | None:
        return await self.crud.get_by_name(name, include_removed)

    async def get_by_room_id(
            self, room_id: int,
            include_removed: bool = False
    ) -> MiniServiceModel | None:
        return await self.crud.get_by_room_id(room_id, include_removed)

    async def get_by_reservation_service_id(
            self,
            reservation_service_id: UUID,
            include_removed: bool = False
    ) -> list[Row[MiniServiceModel]] | None:
        return await self.crud.get_by_reservation_service_id(reservation_service_id,
                                                             include_removed)
