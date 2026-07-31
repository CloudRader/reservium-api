"""
Domain mapper for converting between Pydantic Schemas and Domain Entities for MiniService.

This mapper is responsible for the conversion logic between the presentation layer
and the domain application layer.
"""

import dataclasses
from dataclasses import dataclass
from typing import final

from application.mappers.base import SchemaEntityMapper
from application.schemas import MiniServiceCreate, MiniServiceSchema, MiniServiceUpdate
from domain.entities import MiniService


@final
@dataclass(frozen=True, slots=True)
class MiniServiceMapper(
    SchemaEntityMapper[MiniService, MiniServiceCreate, MiniServiceUpdate, MiniServiceSchema]
):
    """Mapper for converting between MiniService Domain Entities and Pydantic Schemas."""

    def to_entity(self, schema: MiniServiceCreate) -> MiniService:
        return MiniService(
            name=schema.name,
            reservation_service_id=schema.reservation_service_id,
        )

    def update_entity(self, entity: MiniService, schema: MiniServiceUpdate) -> MiniService:
        name = schema.name if schema.name is not None else entity.name
        return dataclasses.replace(entity, name=name)

    def to_schema(self, entity: MiniService) -> MiniServiceSchema:
        return MiniServiceSchema(
            id=entity.id,
            deleted_at=entity.deleted_at,
            name=entity.name,
            reservation_service_id=entity.reservation_service_id,
        )
