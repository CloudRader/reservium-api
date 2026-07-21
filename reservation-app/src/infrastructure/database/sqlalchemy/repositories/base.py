"""
SQLAlchemy implementation of the RepositoryBase port.

This class adapts the generic RepositoryBase port to SQLAlchemy, handling
actual database operations asynchronously. Services depend on the RepositoryBase
interface, not on this concrete implementation.
"""

from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID

from application.ports.repositories import BaseRepository
from domain.entities import BaseEntity
from infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class DBMapper[DbModel, DomainEntity](Protocol):
    """Protocol defining the interface for database mappers."""

    def to_entity(self, model: DbModel) -> DomainEntity:
        """Map database model to domain entity."""
        ...

    def to_model(self, entity: DomainEntity, target: DbModel | None = None) -> DbModel:
        """Map domain entity to database model."""
        ...


class SQLAlchemyBaseRepository[DomainEntity: BaseEntity](BaseRepository[DomainEntity]):
    """Adapter implementing RepositoryBase with SQLAlchemy."""

    def __init__(
        self,
        model: type[Base],
        db: AsyncSession,
        mapper: DBMapper[Any, DomainEntity],
    ):
        self.model: type[Any] = model
        self.db: AsyncSession = db
        self.mapper: DBMapper[Any, DomainEntity] = mapper

    async def get(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> DomainEntity | None:
        stmt = (
            select(self.model)
            .execution_options(include_deleted=include_removed)
            .filter(self.model.id == id_)
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return self.mapper.to_entity(db_obj) if db_obj else None

    async def get_list(
        self, skip: int = 0, limit: int = 10, *, include_removed: bool = False
    ) -> list[DomainEntity]:
        stmt = (
            select(self.model)
            .execution_options(include_deleted=include_removed)
            .order_by(self.model.id.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return [self.mapper.to_entity(obj) for obj in result.scalars().all()]

    async def get_all(self, include_removed: bool = False) -> list[DomainEntity]:
        stmt = select(self.model).execution_options(include_deleted=include_removed)
        result = await self.db.execute(stmt)
        return [self.mapper.to_entity(obj) for obj in result.scalars().all()]

    async def create(self, entity: DomainEntity) -> DomainEntity:
        db_obj = self.mapper.to_model(entity)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return self.mapper.to_entity(db_obj)

    async def create_bulk(self, entities: list[DomainEntity]) -> list[DomainEntity]:
        if not entities:
            return []

        db_objs = [self.mapper.to_model(entity) for entity in entities]

        self.db.add_all(db_objs)
        await self.db.flush()
        await self.db.commit()
        return [self.mapper.to_entity(obj) for obj in db_objs]

    async def update(self, *, entity: DomainEntity) -> DomainEntity:
        stmt = (
            select(self.model)
            .filter(self.model.id == entity.id)
            .execution_options(include_deleted=True)
        )
        result = await self.db.execute(stmt)
        db_model_obj = result.scalar_one()

        self.mapper.to_model(entity, target=db_model_obj)

        self.db.add(db_model_obj)
        await self.db.commit()
        await self.db.refresh(db_model_obj)
        return self.mapper.to_entity(db_model_obj)

    async def restore(
        self,
        obj: DomainEntity,
    ) -> DomainEntity:
        stmt = (
            select(self.model)
            .filter(self.model.id == obj.id)
            .execution_options(include_deleted=True)
        )
        result = await self.db.execute(stmt)
        db_model_obj = result.scalar_one()
        db_model_obj.deleted_at = None
        self.db.add(db_model_obj)
        await self.db.commit()
        return self.mapper.to_entity(db_model_obj)

    async def remove(self, id_: UUID) -> None:
        stmt = (
            select(self.model).execution_options(include_deleted=True).filter(self.model.id == id_)
        )
        result = await self.db.execute(stmt)
        obj = result.scalar_one()
        await self.db.delete(obj)
        await self.db.commit()

    async def soft_remove(self, obj: DomainEntity) -> DomainEntity:
        stmt = (
            select(self.model)
            .filter(self.model.id == obj.id)
            .execution_options(include_deleted=True)
        )
        result = await self.db.execute(stmt)
        db_model_obj = result.scalar_one()
        db_model_obj.deleted_at = datetime.now(UTC)
        self.db.add(db_model_obj)
        await self.db.commit()
        return self.mapper.to_entity(db_model_obj)

    async def count(self, *, include_removed: bool = False) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .execution_options(include_deleted=include_removed)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
