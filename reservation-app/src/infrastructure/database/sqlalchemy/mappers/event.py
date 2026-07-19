"""
Database mapper for converting between Domain Entities and SQLAlchemy Models.

This mapper is responsible for the conversion logic between the domain layer
and the database persistence layer, following the Single Responsibility Principle.
"""

from dataclasses import dataclass
from typing import final

from domain.entities import Event
from infrastructure.database.sqlalchemy.models import EventModel


@final
@dataclass(frozen=True, slots=True)
class EventDBMapper:
    """
    Mapper for converting between Event (Domain) and EventModel (SQLAlchemy).

    This class provides methods for bidirectional mapping, ensuring separation of concerns
    between the domain logic and database persistence.
    """

    def to_entity(self, model: EventModel) -> Event:
        """
        Convert an SQLAlchemy EventModel to a Domain Event.

        :param model: The SQLAlchemy EventModel instance.
        :return: An Event instance.
        """
        return Event(
            id=model.id,
            provider_id=model.provider_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            user_id=model.user_id,
            calendar_id=model.calendar_id,
            reservation_start=model.reservation_start,
            reservation_end=model.reservation_end,
            requested_reservation_start=model.requested_reservation_start,
            requested_reservation_end=model.requested_reservation_end,
            purpose=model.purpose,
            guests=model.guests,
            email=model.email,
            event_state=model.event_state,
            additional_services=model.additional_services,
        )
