"""
Define an abstract base class AbstractMiniServiceService.

This class works with Mini Service.
"""

from abc import ABC, abstractmethod
from typing import Annotated

from core import db_session
from core.application.exceptions import BaseAppError, PermissionDeniedError
from core.schemas import (
    CalendarUpdate,
    MiniServiceCreate,
    MiniServiceDetail,
    MiniServiceLite,
    MiniServiceUpdate,
    UserLite,
)
from crud import CRUDCalendar, CRUDMiniService, CRUDReservationService
from fastapi import Depends
from services import CrudServiceBase
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
    ) -> MiniServiceDetail | None:
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
    ) -> MiniServiceDetail | None:
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
        id_: str | int | None,
        user: UserLite,
    ) -> MiniServiceDetail | None:
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
    ) -> MiniServiceDetail | None:
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
        self.calendar_crud = CRUDCalendar(db)
        self.reservation_service_crud = CRUDReservationService(db)
        super().__init__(CRUDMiniService(db))

    async def create_with_permission_checks(
        self,
        mini_service_create: MiniServiceCreate,
        user: UserLite,
    ) -> MiniServiceDetail | None:
        if await self.crud.get_by_name(mini_service_create.name, True):
            raise BaseAppError("A reservation service with this name already exist.")

        reservation_service = await self.reservation_service_crud.get(
            mini_service_create.reservation_service_id,
        )

        if reservation_service is None:
            raise BaseAppError("A reservation service of mini service isn't exist.")
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
    ) -> MiniServiceDetail | None:
        mini_service_to_update = await self.get(id_)

        if mini_service_to_update is None:
            return None

        reservation_service = await self.reservation_service_crud.get(
            mini_service_to_update.reservation_service_id,
        )

        if reservation_service is None:
            raise BaseAppError("A reservation service of mini service isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to update mini services.",
            )

        return await self.update(id_, mini_service_update)

    async def restore_with_permission_checks(
        self,
        id_: str | int | None,
        user: UserLite,
    ) -> MiniServiceDetail | None:
        mini_service = await self.crud.get(id_, True)

        if mini_service.deleted_at is None:
            raise BaseAppError("A mini service was not soft deleted.")

        reservation_service = await self.reservation_service_crud.get(
            str(mini_service.reservation_service_id),
        )

        if reservation_service is None:
            raise BaseAppError("A reservation service of mini service isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to retrieve mini services.",
            )

        return await self.crud.retrieve_removed_object(id_)

    async def delete_with_permission_checks(
        self,
        id_: str,
        user: UserLite,
        hard_remove: bool = False,
    ) -> MiniServiceDetail | None:
        mini_service = await self.crud.get(id_, True)

        if mini_service is None:
            return None

        if hard_remove and not user.section_head:
            raise PermissionDeniedError(
                "You must be the head of PS to totally delete mini services.",
            )

        reservation_service = await self.reservation_service_crud.get(
            mini_service.reservation_service_id,
        )

        if reservation_service is None:
            raise BaseAppError("A reservation service of mini service isn't exist.")
        if reservation_service.alias not in user.roles:
            raise PermissionDeniedError(
                f"You must be the {reservation_service.name} manager to delete mini services.",
            )

        for calendar in reservation_service.calendars:
            if mini_service.name in calendar.mini_services:
                list_of_mini_services = calendar.mini_services.copy()
                list_of_mini_services.remove(mini_service.name)
                update_exist_calendar = CalendarUpdate(
                    mini_services=list_of_mini_services,
                )
                await self.calendar_crud.update(
                    db_obj=calendar,
                    obj_in=update_exist_calendar,
                )

        if hard_remove:
            return await self.crud.remove(id_)

        return await self.crud.soft_remove(id_)

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
