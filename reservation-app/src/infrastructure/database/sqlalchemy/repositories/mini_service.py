"""
Define CRUD operations for the MiniService model.

Includes an abstract base class (AbstractCRUDMiniService) and a concrete
implementation (CRUDMiniService) using SQLAlchemy.
"""

from uuid import UUID

from application.ports.repositories import MiniServiceRepository
from application.schemas import MiniServiceCreate, MiniServiceUpdate
from infrastructure.database.sqlalchemy.models import MiniServiceModel
from infrastructure.database.sqlalchemy.repositories.base import SQLAlchemyBaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyMiniServiceRepository(
    SQLAlchemyBaseRepository[MiniServiceModel, MiniServiceCreate, MiniServiceUpdate],
    MiniServiceRepository,
):
    """
    Concrete class for CRUD operations specific to the MiniService model.

    It extends the abstract AbstractCRUDMiniService class and implements
    the required methods for querying and manipulating MiniService instances.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(MiniServiceModel, db)

    async def get_by_name(
        self,
        name: str,
        include_removed: bool = False,
    ) -> MiniServiceModel | None:
        stmt = select(self.model).where(self.model.name == name)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_room_id(
        self,
        room_id: int,
        include_removed: bool = False,
    ) -> MiniServiceModel | None:
        stmt = select(self.model).where(self.model.room_id == room_id)
        if include_removed:
            stmt = stmt.execution_options(include_deleted=True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_names_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
    ) -> list[str]:
        stmt = select(self.model.name).where(
            self.model.reservation_service_id == reservation_service_id,
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_ids_by_reservation_service_id(
        self,
        reservation_service_id: UUID,
    ) -> list[UUID]:
        stmt = select(self.model.id).where(
            self.model.reservation_service_id == reservation_service_id,
        )
        result = await self.db.execute(stmt)
        return [row[0] for row in result.fetchall()]
