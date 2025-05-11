"""
This module defines the CRUD operations for the ReservationService model, including an
abstract base class (AbstractCRUDReservationService) and a concrete implementation
(CRUDReservationService) using SQLAlchemy.
"""
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import ReservationServiceModel
from schemas import ReservationServiceCreate, ReservationServiceUpdate

from crud import CRUDBase


class AbstractCRUDReservationService(CRUDBase[
                                         ReservationServiceModel,
                                         ReservationServiceCreate,
                                         ReservationServiceUpdate
                                     ], ABC):
    """
    Abstract class for CRUD operations specific to the ReservationService model.
    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating ReservationService instances.
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
    async def get_by_alias(self, alias: str,
                           include_removed: bool = False) -> ReservationServiceModel | None:
        """
        Retrieves a Reservation Services instance by its service alias.

        :param alias: The alias of the Reservation Service.
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
    async def get_all_aliases(self) -> list[str]:
        """
        Retrieves all aliases from all Reservation Services.

        :return: list of aliases.
        """

    @abstractmethod
    async def get_public_services(
            self, include_removed: bool = False
    ) -> list[ReservationServiceModel]:
        """
        Retrieves a public Reservation Service instance.

        :param include_removed: Include removed object or not.

        :return: The public Reservation Service instance if found, None otherwise.
        """


class CRUDReservationService(AbstractCRUDReservationService):
    """
    Concrete class for CRUD operations specific to the ReservationService model.
    It extends the abstract AbstractCRUDReservationService class and implements
    the required methods for querying and manipulating ReservationService instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(ReservationServiceModel, db)

    async def get_by_name(self, name: str,
                          include_removed: bool = False) -> ReservationServiceModel | None:
        stmt = select(self.model).filter(self.model.name == name)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_alias(self, alias: str,
                           include_removed: bool = False) -> ReservationServiceModel | None:
        stmt = select(self.model).filter(self.model.alias == alias)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_room_id(
            self, room_id: int,
            include_removed: bool = False
    ) -> ReservationServiceModel | None:
        stmt = select(self.model).filter(self.model.room_id == room_id)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_aliases(self) -> list[str]:
        stmt = select(self.model.alias)
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_public_services(
            self, include_removed: bool = False
    ) -> list[ReservationServiceModel]:
        stmt = select(self.model).filter(self.model.public)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
