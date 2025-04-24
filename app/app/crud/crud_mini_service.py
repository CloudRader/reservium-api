"""
This module defines the CRUD operations for the MiniService model, including an
abstract base class (AbstractCRUDMiniService) and a concrete implementation (CRUDMiniService)
using SQLAlchemy.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import MiniServiceModel
from schemas import MiniServiceCreate, MiniServiceUpdate

from crud import CRUDBase


class AbstractCRUDMiniService(CRUDBase[
                                  MiniServiceModel,
                                  MiniServiceCreate,
                                  MiniServiceUpdate
                              ], ABC):
    """
    Abstract class for CRUD operations specific to the Calendar model.
    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Calendar instances.
    """

    @abstractmethod
    async def get_by_name(self, name: str,
                    include_removed: bool = False) -> MiniServiceModel | None:
        """
        Retrieves a Calendar instance by its name.

        :param name: The name of the Mini Service.
        :param include_removed: Include removed object or not.

        :return: The Mini Service instance if found, None otherwise.
        """

    @abstractmethod
    async def get_names_by_reservation_service_id(
            self, reservation_service_id: UUID
    ) -> list[str]:
        """
        Retrieves all names from all Mini Services
        by reservation service uuid.

        :param reservation_service_id: The uuid of the reservation service.

        :return: list of aliases.
        """


class CRUDMiniService(AbstractCRUDMiniService):
    """
    Concrete class for CRUD operations specific to the Calendar model.
    It extends the abstract AbstractCRUDCalendar class and implements the required methods
    for querying and manipulating Calendar instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(MiniServiceModel, db)

    async def get_by_name(self, name: str,
                    include_removed: bool = False) -> MiniServiceModel | None:
        stmt = select(self.model).where(self.model.name == name)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_names_by_reservation_service_id(
            self, reservation_service_id: UUID
    ) -> list[str]:
        stmt = select(self.model.name).where(
            self.model.reservation_service_id == reservation_service_id
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]
