"""
Domain mapper for converting between Pydantic Schemas and Domain Entities.

This mapper is responsible for the conversion logic between the presentation layer
and the domain application layer.
"""

import dataclasses
from dataclasses import dataclass
from typing import final

from application.mappers.base import SchemaEntityMapper
from application.schemas import (
    ReservationServiceCreate,
    ReservationServiceLite,
    ReservationServiceUpdate,
)
from domain.entities import ReservationService


@final
@dataclass(frozen=True, slots=True)
class ReservationServiceMapper(
    SchemaEntityMapper[
        ReservationService,
        ReservationServiceCreate,
        ReservationServiceUpdate,
        ReservationServiceLite,
    ]
):
    """
    Mapper for converting between Domain Entities and Pydantic Schemas.

    This mapper is part of the Application layer and handles conversions between:
    - Domain Entities (business logic)
    - Pydantic Schemas (service data transfer)
    """

    def to_entity(self, schema: ReservationServiceCreate) -> ReservationService:
        return ReservationService(
            name=schema.name,
            alias=schema.alias,
            contact_mail=schema.contact_mail,
            public=schema.public,
            web=schema.web,
        )

    def update_entity(
        self, entity: ReservationService, schema: ReservationServiceUpdate
    ) -> ReservationService:
        name = schema.name if schema.name is not None else entity.name
        alias = schema.alias if schema.alias is not None else entity.alias
        contact_mail = (
            schema.contact_mail if schema.contact_mail is not None else entity.contact_mail
        )
        public = schema.public if schema.public is not None else entity.public
        web = schema.web if schema.web is not None else entity.web

        return dataclasses.replace(
            entity,
            name=name,
            alias=alias,
            contact_mail=contact_mail,
            public=public,
            web=web,
        )

    def to_schema(self, entity: ReservationService) -> ReservationServiceLite:
        return ReservationServiceLite(
            id=entity.id,
            name=entity.name,
            alias=entity.alias,
            contact_mail=entity.contact_mail,
            public=entity.public,
            web=entity.web,
        )
