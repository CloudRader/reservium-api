"""
Database mapper for converting between Domain Entities and SQLAlchemy Models.

This mapper is responsible for the conversion logic between the domain layer
and the database persistence layer, following the Single Responsibility Principle.
"""

from dataclasses import dataclass
from typing import final

from domain.entities import User
from infrastructure.database.sqlalchemy.models import UserModel


@final
@dataclass(frozen=True, slots=True)
class UserDBMapper:
    """
    Mapper for converting between User (Domain) and UserModel (SQLAlchemy).

    This class provides methods for bidirectional mapping, ensuring separation of concerns
    between the domain logic and database persistence.
    """

    def to_entity(self, model: UserModel) -> User:
        """
        Convert an SQLAlchemy UserModel to a Domain User.

        :param model: The SQLAlchemy UserModel instance.
        :return: A User instance.
        """
        roles = []
        if model.roles:
            roles = model.roles
        return User(
            id=model.id,
            provider_id=model.provider_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            username=model.username,
            full_name=model.full_name,
            active_member=model.active_member,
            roles=roles,
        )
