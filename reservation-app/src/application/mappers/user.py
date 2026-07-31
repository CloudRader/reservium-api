"""
Domain mapper for converting between Pydantic Schemas and Domain Entities for User.

This mapper is responsible for the conversion logic between the presentation layer
and the domain application layer.
"""

import dataclasses
from dataclasses import dataclass
from typing import final

from application.mappers.base import SchemaEntityMapper
from application.schemas import UserCreate, UserSchema, UserUpdate
from domain.entities import User


@final
@dataclass(frozen=True, slots=True)
class UserMapper(SchemaEntityMapper[User, UserCreate, UserUpdate, UserSchema]):
    """Mapper for converting between User Domain Entities and Pydantic Schemas."""

    def to_entity(self, schema: UserCreate) -> User:
        return User(
            username=schema.username,
            full_name=schema.full_name,
            provider_id=schema.provider_id,
            active_member=schema.active_member,
            roles=schema.roles,
        )

    def update_entity(self, entity: User, schema: UserUpdate) -> User:
        username = schema.username if schema.username is not None else entity.username
        full_name = schema.full_name if schema.full_name is not None else entity.full_name
        provider_id = schema.provider_id if schema.provider_id is not None else entity.provider_id
        active_member = (
            schema.active_member if schema.active_member is not None else entity.active_member
        )
        roles = schema.roles if schema.roles is not None else entity.roles

        return dataclasses.replace(
            entity,
            username=username,
            full_name=full_name,
            provider_id=provider_id,
            active_member=active_member,
            roles=roles,
        )

    def to_schema(self, entity: User) -> UserSchema:
        return UserSchema(
            id=entity.id,
            deleted_at=entity.deleted_at,
            username=entity.username,
            full_name=entity.full_name,
            provider_id=entity.provider_id,
            active_member=entity.active_member,
            roles=entity.roles,
        )
