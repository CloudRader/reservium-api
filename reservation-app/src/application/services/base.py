"""
Define abstract and concrete base application services.

This module provides generic application services that orchestrate domain entities,
repository ports, and presentation DTO mappers following Domain-Driven Design (DDD)
and Clean Architecture principles.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from application.mappers import SchemaEntityMapper
from application.ports.repositories import BaseRepository
from core.bootstrap.exceptions import BaseAppError, Entity, EntityNotFoundError
from domain.entities import BaseEntity
from pydantic import BaseModel


class AbstractBaseService[
    Schema: BaseModel,
    Repository: BaseRepository,
    DomainEntity: BaseEntity,
    CreateSchema: BaseModel,
    UpdateSchema: BaseModel,
](ABC):
    """
    Abstract base class for application use-case services.

    Defines a contract for application services operating on domain entities and
    translating between presentation-layer DTO schemas and domain representations.
    """

    @abstractmethod
    async def get(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> Schema:
        """
        Retrieve a domain entity by ID and map it to a detailed DTO schema.

        :param id_: The unique identifier of the domain entity.
        :param include_removed: Whether to include soft-deleted entities.
        :return: Detailed DTO schema representation of the domain entity.
        """

    @abstractmethod
    async def get_all(self, include_removed: bool = False) -> list[Schema]:
        """
        Retrieve all domain entities and map them to lite DTO schemas.

        :param include_removed: Whether to include soft-deleted entities.
        :return: List of lite DTO schema representations.
        """

    @abstractmethod
    async def create(self, create_schema: CreateSchema) -> Schema:
        """
        Create a new domain entity from an input DTO schema and persist it.

        :param create_schema: Pydantic creation DTO schema.
        :return: Detailed DTO schema representation of the created entity.
        """

    @abstractmethod
    async def update(
        self,
        id_: UUID,
        update_schema: UpdateSchema,
    ) -> Schema:
        """
        Apply updates to an existing domain entity and persist changes.

        :param id_: The unique identifier of the domain entity to update.
        :param update_schema: Pydantic update DTO schema containing modification data.
        :return: Detailed DTO schema representation of the updated entity.
        """

    @abstractmethod
    async def restore(self, id_: UUID) -> Schema:
        """
        Restore a previously soft-removed domain entity by ID.

        :param id_: Unique identifier of the domain entity to restore.
        :return: Detailed DTO schema representation of the restored entity.
        """

    @abstractmethod
    async def soft_delete(self, id_: UUID) -> Schema:
        """
        Soft-delete a domain entity by marking it as deleted.

        :param id_: Unique identifier of the domain entity.
        :return: Detailed DTO schema representation of the soft-deleted entity.
        """

    @abstractmethod
    async def delete(self, id_: UUID) -> None:
        """
        Permanently remove a domain entity from persistence storage.

        :param id_: Unique identifier of the domain entity to delete.
        """


class BaseService[
    Schema: BaseModel,
    Repository: BaseRepository,
    DomainEntity: BaseEntity,
    CreateSchema: BaseModel,
    UpdateSchema: BaseModel,
](AbstractBaseService[Schema, Repository, DomainEntity, CreateSchema, UpdateSchema]):
    """
    Generic application service implementing use-case operations for domain entities.

    Orchestrates interaction between repository ports, domain entity invariants, and
    schema mappers.
    """

    def __init__(
        self,
        repo: Repository,
        entity_name: Entity,
        schema: type[Schema],
        mapper: SchemaEntityMapper,
    ):
        self.repo: Repository = repo
        self.entity_name: Entity = entity_name
        self.schema: type[Schema] = schema
        self.mapper: SchemaEntityMapper = mapper

    async def get(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> Schema:
        entity = await self.repo.get(id_, include_removed)
        if entity is None:
            raise EntityNotFoundError(self.entity_name, id_)
        return self.mapper.to_schema(entity)

    async def get_all(self, include_removed: bool = False) -> list[Schema]:
        entities = await self.repo.get_all(include_removed)
        return [self.mapper.to_schema(entity) for entity in entities]

    async def create(self, create_schema: CreateSchema) -> Schema:
        entity = self.mapper.to_entity(create_schema)
        saved_entity = await self.repo.create(entity)
        return self.mapper.to_schema(saved_entity)

    async def update(
        self,
        id_: UUID,
        update_schema: UpdateSchema,
    ) -> Schema:
        entity = await self.repo.get(id_)
        if entity is None:
            raise EntityNotFoundError(self.entity_name, id_)
        updated_entity = self.mapper.update_entity(entity, update_schema)
        updated = await self.repo.update(updated_entity)
        return self.mapper.to_schema(updated)

    async def restore(self, id_: UUID) -> Schema:
        obj = await self.repo.get(id_, True)
        if obj is None:
            raise EntityNotFoundError(self.entity_name, id_)
        deleted_at = getattr(obj, "deleted_at", None)
        if deleted_at is None:
            message = f"A {self.entity_name.value} was not soft deleted."
            raise BaseAppError(message)
        restored = await self.repo.restore(obj)
        return self.mapper.to_schema(restored)

    async def soft_delete(self, id_: UUID) -> Schema:
        entity = await self.repo.get(id_, True)
        if entity is None:
            raise EntityNotFoundError(self.entity_name, id_)
        deleted_at = getattr(entity, "deleted_at", None)
        if deleted_at is not None:
            message = f"A {self.entity_name.value} is already soft deleted."
            raise BaseAppError(message)
        deleted = await self.repo.soft_remove(entity)
        return self.mapper.to_schema(deleted)

    async def delete(self, id_: UUID) -> None:
        entity = await self.repo.get(id_, True)
        if entity is None:
            raise EntityNotFoundError(self.entity_name, id_)
        await self.repo.remove(id_)
