"""
Domain mapper for converting between Pydantic Schemas and Domain Entities for Calendar.

This mapper is responsible for the conversion logic between the presentation layer
and the domain application layer.
"""

import dataclasses
from dataclasses import dataclass
from typing import final

from application.mappers.base import SchemaEntityMapper
from application.schemas import CalendarCreate, CalendarSchema, CalendarUpdate
from application.schemas import Rules as RulesSchema
from domain.entities import Calendar
from domain.value_objects import Rules


@final
@dataclass(frozen=True, slots=True)
class CalendarMapper(SchemaEntityMapper[Calendar, CalendarCreate, CalendarUpdate, CalendarSchema]):
    """Mapper for converting between Calendar Domain Entities and Pydantic Schemas."""

    def to_entity(self, schema: CalendarCreate) -> Calendar:
        return Calendar(
            reservation_service_id=schema.reservation_service_id,
            reservation_type=schema.reservation_type,
            color=schema.color,
            max_people=schema.max_people,
            more_than_max_people_with_permission=schema.more_than_max_people_with_permission,
            collision_with_itself=schema.collision_with_itself,
            club_member_rules=Rules(**schema.club_member_rules.model_dump()),
            active_member_rules=Rules(**schema.active_member_rules.model_dump()),
            manager_rules=Rules(**schema.manager_rules.model_dump()),
            provider_id=schema.provider_id,
        )

    def update_entity(self, entity: Calendar, schema: CalendarUpdate) -> Calendar:
        color = schema.color if schema.color is not None else entity.color
        more_than_max = (
            schema.more_than_max_people_with_permission
            if schema.more_than_max_people_with_permission is not None
            else entity.more_than_max_people_with_permission
        )
        max_people = schema.max_people if schema.max_people is not None else entity.max_people
        collision_with_itself = (
            schema.collision_with_itself
            if schema.collision_with_itself is not None
            else entity.collision_with_itself
        )
        provider_id = schema.provider_id if schema.provider_id is not None else entity.provider_id

        club_member_rules = (
            schema.club_member_rules
            if schema.club_member_rules is not None
            else entity.club_member_rules
        )
        active_member_rules = (
            schema.active_member_rules
            if schema.active_member_rules is not None
            else entity.active_member_rules
        )
        manager_rules = (
            schema.manager_rules if schema.manager_rules is not None else entity.manager_rules
        )

        return dataclasses.replace(
            entity,
            color=color,
            max_people=max_people,
            more_than_max_people_with_permission=more_than_max,
            collision_with_itself=collision_with_itself,
            club_member_rules=club_member_rules,
            active_member_rules=active_member_rules,
            manager_rules=manager_rules,
            provider_id=provider_id,
        )

    def to_schema(self, entity: Calendar) -> CalendarSchema:
        return CalendarSchema(
            id=entity.id,
            deleted_at=entity.deleted_at,
            reservation_type=entity.reservation_type,
            color=entity.color,
            max_people=entity.max_people,
            more_than_max_people_with_permission=entity.more_than_max_people_with_permission,
            collision_with_itself=entity.collision_with_itself,
            reservation_service_id=entity.reservation_service_id,
            provider_id=entity.provider_id,
            club_member_rules=RulesSchema(**dataclasses.asdict(entity.club_member_rules)),
            active_member_rules=RulesSchema(**dataclasses.asdict(entity.active_member_rules)),
            manager_rules=RulesSchema(**dataclasses.asdict(entity.manager_rules)),
        )
