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
        )

    def to_model(
        self, entity: MiniService, target: MiniServiceModel | None = None
    ) -> MiniServiceModel:
        """
        Convert a Domain MiniService to an SQLAlchemy MiniServiceModel.

        :param entity: The Domain MiniService instance.
        :param target: The target MiniServiceModel instance to update.
        :return: A MiniServiceModel instance.
        """
        if target is None:
            target = MiniServiceModel(id=entity.id)
        target.name = entity.name
        target.reservation_service_id = entity.reservation_service_id
        return target
