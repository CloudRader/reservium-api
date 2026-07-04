"""Custom SQLAlchemy column type for storing `Rules` Pydantic models as JSON."""

from domain.models.types.pydantic_type import PydanticType


class RulesType(PydanticType):
    """
    Custom SQLAlchemy type for serializing and deserializing the `Rules` Pydantic model.

    This type handles conversion of `Rules` objects to and from JSON for database storage.
    """

    @property
    def model_class(self):
        # Local import to break the circular dependency!
        from api.schemas.calendar import Rules

        return Rules
