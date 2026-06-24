"""Custom SQLAlchemy column type for storing `Rules` Pydantic models as JSON."""

from domain.models.types.pydantic_type import PydanticType
from domain.schemas import Rules


class RulesType(PydanticType):
    """
    Custom SQLAlchemy type for serializing and deserializing the `Rules` Pydantic model.

    This type handles conversion of `Rules` objects to and from JSON for database storage.
    """

    model_class = Rules
