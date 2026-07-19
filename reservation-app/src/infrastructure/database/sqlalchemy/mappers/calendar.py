"""
Database mapper for converting between Domain Entities and SQLAlchemy Models.

This mapper is responsible for the conversion logic between the domain layer
and the database persistence layer, following the Single Responsibility Principle.
"""

from dataclasses import dataclass
from typing import final

from domain.entities import Calendar
from infrastructure.database.sqlalchemy.models import CalendarModel


@final
@dataclass(frozen=True, slots=True)
class CalendarDBMapper:
    """
    Mapper for converting between Calendar (Domain) and CalendarModel (SQLAlchemy).

    This class provides methods for bidirectional mapping, ensuring separation of concerns
    between the domain logic and database persistence.
    """

    def to_entity(self, model: CalendarModel) -> Calendar:
        """
        Convert an SQLAlchemy CalendarModel to a Domain Calendar.

        :param model: The SQLAlchemy CalendarModel instance.
        :return: A Calendar instance.
        """
        return Calendar(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            reservation_service_id=model.reservation_service_id,
            provider_id=model.provider_id,
            reservation_type=model.reservation_type,
            color=model.color,
            max_people=model.max_people,
            more_than_max_people_with_permission=model.more_than_max_people_with_permission,
            collision_with_itself=model.collision_with_itself,
            club_member_rules=model.club_member_rules,
            active_member_rules=model.active_member_rules,
            manager_rules=model.manager_rules,
            collision_ids=model.collision_ids,
            mini_service_ids=[c.id for c in model.mini_services or []],
        )
