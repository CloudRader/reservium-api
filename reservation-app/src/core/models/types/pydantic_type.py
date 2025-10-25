"""Custom SQLAlchemy type for storing Pydantic models as JSON in TEXT columns."""

import json
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic.json import pydantic_encoder
from sqlalchemy.types import TEXT, TypeDecorator

T = TypeVar("T", bound=BaseModel)


class PydanticType[T: BaseModel](TypeDecorator):
    """SQLAlchemy type for persisting `Rules` Pydantic models as JSON in the database."""

    impl = TEXT
    model_class: type[T]  # To be defined in subclasses

    @property
    def python_type(self) -> type[Any]:
        return self.model_class

    def load_dialect_impl(self, dialect):  # noqa: ARG002
        return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value, dialect):  # noqa: ARG002
        if value is None:
            return None
        if isinstance(value, dict):
            value = self.model_class(**value)
        return json.dumps(value.model_dump(), default=pydantic_encoder)

    def process_result_value(self, value, dialect):  # noqa: ARG002
        if value is None:
            return None
        return self.model_class.model_validate_json(value)

    def process_literal_param(self, value, dialect):  # noqa: ARG002
        if value is None:
            return None
        if isinstance(value, dict):
            value = self.model_class(**value)
        return json.dumps(value.model_dump())

    def copy(self, **kw):  # noqa: ARG002
        return type(self)(self.impl)
