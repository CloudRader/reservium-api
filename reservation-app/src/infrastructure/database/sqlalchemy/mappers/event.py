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
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            provider_id=model.provider_id,
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

    def to_model(self, entity: Event, target: EventModel | None = None) -> EventModel:
        """
        Convert a Domain Event to an SQLAlchemy EventModel.

        :param entity: The Domain Event instance.
        :param target: The target EventModel instance to update.
        :return: An EventModel instance.
        """
        if target is None:
            target = EventModel(id=entity.id)
        target.provider_id = entity.provider_id
        target.user_id = entity.user_id
        target.calendar_id = entity.calendar_id
        target.reservation_start = entity.reservation_start
        target.reservation_end = entity.reservation_end
        target.requested_reservation_start = entity.requested_reservation_start
        target.requested_reservation_end = entity.requested_reservation_end
        target.purpose = entity.purpose
        target.guests = entity.guests
        target.email = entity.email
        target.event_state = entity.event_state
        target.additional_services = entity.additional_services
        return target
