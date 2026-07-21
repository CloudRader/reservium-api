"""
Database mapper for converting between Domain Entities and SQLAlchemy Models.

This mapper is responsible for the conversion logic between the domain layer
and the database persistence layer, following the Single Responsibility Principle.
"""

from dataclasses import dataclass
from typing import final

from domain.entities import ReservationService
from infrastructure.database.sqlalchemy.models import ReservationServiceModel


@final
@dataclass(frozen=True, slots=True)
class ReservationServiceDBMapper:
    """
    DB mapper for ReservationService domain entities.

    This class provides methods for bidirectional mapping, ensuring separation of concerns
    between the domain logic and database persistence.
    """

    def to_entity(self, model: ReservationServiceModel) -> ReservationService:
        """
        Convert an SQLAlchemy ReservationServiceModel to a Domain ReservationService.

        :param model: The SQLAlchemy ReservationServiceModel instance.
        :return: A ReservationService instance.
        """
        return ReservationService(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            name=model.name,
            alias=model.alias,
            contact_mail=model.contact_mail,
            public=model.public,
            web=model.web,
        )

    def to_model(
        self, entity: ReservationService, target: ReservationServiceModel | None = None
    ) -> ReservationServiceModel:
        """
        Convert a Domain ReservationService to an SQLAlchemy ReservationServiceModel.

        :param entity: The Domain ReservationService instance.
        :param target: The target ReservationServiceModel instance to update.
        :return: A ReservationServiceModel instance.
        """
        if target is None:
            target = ReservationServiceModel(id=entity.id)
        target.name = entity.name
        target.alias = entity.alias
        target.contact_mail = entity.contact_mail
        target.public = entity.public
        target.web = entity.web
        return target
