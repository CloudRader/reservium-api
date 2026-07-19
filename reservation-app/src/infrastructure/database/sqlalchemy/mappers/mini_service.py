"""
Database mapper for converting between Domain Entities and SQLAlchemy Models.

This mapper is responsible for the conversion logic between the domain layer
and the database persistence layer, following the Single Responsibility Principle.
"""

from dataclasses import dataclass
from typing import final

from domain.entities import MiniService
from infrastructure.database.sqlalchemy.models import MiniServiceModel


@final
@dataclass(frozen=True, slots=True)
class MiniServiceDBMapper:
    """
    Mapper for converting between MiniService (Domain) and MiniServiceModel (SQLAlchemy).

    This class provides methods for bidirectional mapping, ensuring separation of concerns
    between the domain logic and database persistence.
    """

    def to_entity(self, model: MiniServiceModel) -> MiniService:
        """
        Convert an SQLAlchemy MiniServiceModel to a Domain MiniService.

        :param model: The SQLAlchemy MiniServiceModel instance.
        :return: A MiniService instance.
        """
        return MiniService(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            name=model.name,
            reservation_service_id=model.reservation_service_id,
            access_group=model.access_group,
            room_id=model.room_id,
            lockers_id=model.lockers_id,
            calendar_ids=[c.id for c in model.calendars or []],
        )
