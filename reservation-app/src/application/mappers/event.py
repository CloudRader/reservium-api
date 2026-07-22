"""
Domain mapper for converting between Pydantic Schemas and Domain Entities for Event.

This mapper is responsible for the conversion logic between the presentation layer
and the domain application layer.
"""

import dataclasses
from dataclasses import dataclass
from typing import final
from uuid import UUID

from application.mappers.base import SchemaEntityMapper
from application.schemas import EventCreate, EventLite, EventUpdate
from domain.entities import Event


@final
@dataclass(frozen=True, slots=True)
class EventMapper(SchemaEntityMapper[Event, EventCreate, EventUpdate, EventLite]):
    """Mapper for converting between Event Domain Entities and Pydantic Schemas."""

    def to_entity(self, schema: EventCreate, *, user_id: UUID) -> Event:
        return Event(
            user_id=user_id,
            reservation_start=schema.start_datetime,
            reservation_end=schema.end_datetime,
            purpose=schema.purpose,
            guests=schema.guests,
            email=schema.email,
            calendar_id=schema.calendar_id,
            additional_services=schema.additional_services,
        )

    def update_entity(self, entity: Event, schema: EventUpdate) -> Event:
        reservation_start = (
            schema.reservation_start
            if schema.reservation_start is not None
            else entity.reservation_start
        )
        reservation_end = (
            schema.reservation_end if schema.reservation_end is not None else entity.reservation_end
        )
        purpose = schema.purpose if schema.purpose is not None else entity.purpose
        guests = schema.guests if schema.guests is not None else entity.guests
        email = schema.email if schema.email is not None else entity.email
        event_state = schema.event_state if schema.event_state is not None else entity.event_state
        additional_services = (
            schema.additional_services
            if schema.additional_services is not None
            else entity.additional_services
        )

        return dataclasses.replace(
            entity,
            reservation_start=reservation_start,
            reservation_end=reservation_end,
            purpose=purpose,
            guests=guests,
            email=email,
            event_state=event_state,
            additional_services=additional_services,
        )

    def to_schema(self, entity: Event) -> EventLite:
        return EventLite(
            id=entity.id,
            user_id=entity.user_id,
            calendar_id=entity.calendar_id,
            reservation_start=entity.reservation_start,
            reservation_end=entity.reservation_end,
            purpose=entity.purpose,
            guests=entity.guests,
            email=entity.email,
            event_state=entity.event_state,
            additional_services=entity.additional_services,
        )
