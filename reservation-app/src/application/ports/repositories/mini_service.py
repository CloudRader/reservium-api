"""
Define CRUD operations for the MiniService model.

Includes an abstract base class (AbstractCRUDMiniService) and a concrete
implementation (CRUDMiniService) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from api.schemas import MiniServiceCreate, MiniServiceUpdate
from application.ports.repositories import BaseRepository
from infrastructure.database.sqlalchemy.models import MiniServiceModel


class MiniServiceRepository(
    BaseRepository[MiniServiceModel, MiniServiceCreate, MiniServiceUpdate],
    ABC,
):
    """
    Abstract class for CRUD operations specific to the MiniService model.

    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating MiniService instances.
    """

    @abstractmethod
    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniServiceModel | None:
        """
        Retrieve a MiniService instance by its name.

        :param name: The name of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> MiniServiceModel | None:
        """
        Retrieve a Mini Service instance by its room id.

        :param room_id: The room id of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_names_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
    ) -> list[str]:
        """
        Retrieve all names from all Mini Services by reservation service uuid.

        :param reservation_service_id: The uuid of the reservation service.

        :return: list of names.
        """

    @abstractmethod
    async def get_ids_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
    ) -> list[UUID]:
        """
        Retrieve all ids from all Mini Services by reservation service uuid.

        :param reservation_service_id: The uuid of the reservation service.

        :return: list of ids.
        """
