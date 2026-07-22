"""Base protocol for Application layer mapper (Domain Entity <-> Pydantic Schema)."""

from abc import abstractmethod
from typing import Protocol


class SchemaEntityMapper[DomainEntity, CreateSchema, UpdateSchema, Schema](Protocol):
    """Protocol for Application layer mapper (Domain Entity <-> Pydantic Schema)."""

    @abstractmethod
    def to_entity(self, schema: CreateSchema) -> DomainEntity:
        """
        Convert Pydantic CreateSchema to Domain Entity.

        :param schema: The Pydantic CreateSchema instance.
        :return: A Domain Entity instance.
        """

    @abstractmethod
    def update_entity(self, entity: DomainEntity, schema: UpdateSchema) -> DomainEntity:
        """
        Update a Domain Entity with values from a Pydantic UpdateSchema.

        :param entity: The Domain Entity instance to update.
        :param schema: The Pydantic UpdateSchema instance.
        :return: The updated Domain Entity instance.
        """

    @abstractmethod
    def to_schema(self, entity: DomainEntity) -> Schema:
        """
        Convert a Domain Entity to a Pydantic Schema.

        :param entity: The Domain Entity instance to convert.
        :return: The converted Pydantic Schema instance.
        """
