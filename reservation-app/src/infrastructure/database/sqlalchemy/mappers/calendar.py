"""
Database mapper for converting between Domain Entities and SQLAlchemy Models.

This mapper is responsible for the conversion logic between the domain layer
and the database persistence layer, following the Single Responsibility Principle.
"""

from dataclasses import dataclass
from typing import Any, final

from domain.entities import Calendar
from domain.value_objects import Rules
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

        def _to_domain_rules(rules: Any) -> Rules:
            if isinstance(rules, Rules):
                return rules
            if hasattr(rules, "model_dump"):
                return Rules(**rules.model_dump())
            if isinstance(rules, dict):
                return Rules(**rules)
            return rules

        return Calendar(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            provider_id=model.provider_id,
            reservation_service_id=model.reservation_service_id,
            reservation_type=model.reservation_type,
            color=model.color,
            max_people=model.max_people,
            more_than_max_people_with_permission=model.more_than_max_people_with_permission,
            collision_with_itself=model.collision_with_itself,
            club_member_rules=_to_domain_rules(model.club_member_rules),
            active_member_rules=_to_domain_rules(model.active_member_rules),
            manager_rules=_to_domain_rules(model.manager_rules),
        )

    def to_model(self, entity: Calendar, target: CalendarModel | None = None) -> CalendarModel:
        """
        Convert a Domain Calendar to an SQLAlchemy CalendarModel.

        :param entity: The Domain Calendar instance.
        :param target: The target CalendarModel instance to update.
        :return: A CalendarModel instance.
        """
        if target is None:
            target = CalendarModel(id=entity.id)
        target.provider_id = entity.provider_id
        target.reservation_service_id = entity.reservation_service_id
        target.reservation_type = entity.reservation_type
        target.color = entity.color
        target.max_people = entity.max_people
        target.more_than_max_people_with_permission = entity.more_than_max_people_with_permission
        target.collision_with_itself = entity.collision_with_itself
        target.club_member_rules = entity.club_member_rules
        target.active_member_rules = entity.active_member_rules
        target.manager_rules = entity.manager_rules
        return target
