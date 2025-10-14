"""
Define an abstract base class AbstractMiniServiceService.

This class works with Mini Service.
"""

from abc import ABC, abstractmethod
from typing import Annotated

from core import db_session
from core.application.exceptions import (
    Entity,
    EntityNotFoundError,
)
from core.schemas import (
    MiniServiceCreate,
    MiniServiceDetail,
    MiniServiceLite,
    MiniServiceUpdate,
    ReservationServiceDetail,
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
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniServiceDetail:
        """
        Retrieve a Mini Service instance by its name.

        :param name: The name of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance.
        """

    @abstractmethod
    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> MiniServiceDetail:
        """
        Retrieve a Mini Service instance by its room id.

        :param room_id: The room id of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance.
        """

    @abstractmethod
    async def get_reservation_service(
        self,
        id_: str,
    ) -> ReservationServiceDetail:
        """
        Retrieve the reservation service of this mini service by reservation service id.

        :param id_: The id of the mini service.

        :return: Reservation Service of this mini service if found.
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

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniServiceDetail:
        mini_service = await self.crud.get_by_name(name, include_removed)
        if mini_service is None:
            raise EntityNotFoundError(self.entity_name, name)
        return mini_service

    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> MiniServiceDetail:
        mini_service = await self.crud.get_by_room_id(room_id, include_removed)
        if mini_service is None:
            raise EntityNotFoundError(self.entity_name, room_id)
        return mini_service

    async def get_reservation_service(
        self,
        id_: str,
    ) -> ReservationServiceDetail:
        mini_service = await self.get(id_, True)
        return await self.reservation_service_service.get(mini_service.reservation_service_id, True)
