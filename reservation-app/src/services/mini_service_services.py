"""
Define an abstract base class AbstractMiniServiceService.

This class works with Mini Service.
"""

from abc import ABC, abstractmethod
from typing import Annotated

from core import db_session
from core.application.exceptions import BaseAppError, Entity, PermissionDeniedError
from core.schemas import (
    MiniServiceCreate,
    MiniServiceDetail,
    MiniServiceLite,
    MiniServiceUpdate,
    UserLite,
)
from crud import CRUDCalendar, CRUDMiniService
from fastapi import Depends
from services import CrudServiceBase
from services.reservation_service_services import ReservationServiceService
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractMiniServiceService(
    CrudServiceBase[
        MiniServiceLite,
        MiniServiceDetail,
        CRUDMiniService,
        MiniServiceCreate,
        MiniServiceUpdate,
    ],
    ABC,
):
    """
    Abstract class defines the interface for a mini service ser.

    Provides CRUD operations for a specific MiniServiceModel.
    """

    @abstractmethod
    async def create_with_permission_checks(
        self,
        mini_service_create: MiniServiceCreate,
        user: UserLite,
    ) -> MiniServiceDetail:
        """
        Create a Mini Service in the database.

        :param mini_service_create: MiniServiceCreate SchemaLite for create.
        :param user: the UserSchema for control permissions of the mini service.

        :return: the created Mini Service.
        """

    @abstractmethod
    async def update_with_permission_checks(
        self,
        id_: str,
        mini_service_update: MiniServiceUpdate,
        user: UserLite,
    ) -> MiniServiceDetail:
        """
        Update a Mini Service in the database.

        :param id_: The id of the Mini Service.
        :param mini_service_update: MiniServiceUpdate SchemaLite for update.
        :param user: the UserSchema for control permissions of the mini service.

        :return: the updated Mini Service.
        """

    @abstractmethod
    async def restore_with_permission_checks(
        self,
        id_: str | int,
        user: UserLite,
    ) -> MiniServiceDetail:
        """
        Retrieve removed mini service from soft removed.

        :param id_: The id of the mini service to retrieve from removed.
        :param user: the UserSchema for control permissions of the mini service.

        :return: the updated Mini Service.
        """

    @abstractmethod
    async def delete_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
        hard_remove: bool = False,
    ) -> MiniServiceDetail:
        """
        Delete a Mini Service in the database.

        :param id_: The id of the Mini Service.
        :param user: the UserSchema for control permissions of the mini service.
        :param hard_remove: hard remove of the reservation service or not.

        :return: the deleted Mini Service.
        """

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniServiceDetail | None:
        """
        Retrieve a Mini Service instance by its name.

        :param name: The name of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> MiniServiceDetail | None:
        """
        Retrieve a Mini Service instance by its room id.

        :param room_id: The room id of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance if found, None otherwise.
        """


class MiniServiceService(AbstractMiniServiceService):
    """Class MiniServiceService represent service that work with Mini Service."""

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(db_session.scoped_session_dependency)],
    ):
        super().__init__(CRUDMiniService(db), Entity.MINI_SERVICE)
        self.calendar_crud = CRUDCalendar(db)
        self.reservation_service_service = ReservationServiceService(db)

    async def create_with_permission_checks(
        self,
        mini_service_create: MiniServiceCreate,
        user: UserLite,
    ) -> MiniServiceDetail:
        if await self.crud.get_by_name(mini_service_create.name, True):
            raise BaseAppError("A reservation service with this name already exist.")

        reservation_service = await self.reservation_service_service.get(
            mini_service_create.reservation_service_id,
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to create mini services.",
            )

        return await self.crud.create(mini_service_create)

    async def update_with_permission_checks(
        self,
        id_: str,
        mini_service_update: MiniServiceUpdate,
        user: UserLite,
    ) -> MiniServiceDetail:
        mini_service_to_update = await self.get(id_)

        reservation_service = await self.reservation_service_service.get(
            mini_service_to_update.reservation_service_id,
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to update mini services.",
            )

        return await self.update(id_, mini_service_update)

    async def restore_with_permission_checks(
        self,
        id_: str | int,
        user: UserLite,
    ) -> MiniServiceDetail:
        mini_service = await self.get(id_, True)

        reservation_service = await self.reservation_service_service.get(
            str(mini_service.reservation_service_id),
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to retrieve mini services.",
            )

        return await self.restore(id_)

    async def delete_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
        hard_remove: bool = False,
    ) -> MiniServiceDetail:
        mini_service = await self.get(id_, True)

        if hard_remove and not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to totally delete mini services.",
            )

        reservation_service = await self.reservation_service_service.get(
            mini_service.reservation_service_id,
        )

        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to delete mini services.",
            )

        if hard_remove:
            return await self.remove(id_)

        return await self.soft_remove(id_)

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniServiceDetail | None:
        return await self.crud.get_by_name(name, include_removed)

    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> MiniServiceDetail | None:
        return await self.crud.get_by_room_id(room_id, include_removed)
