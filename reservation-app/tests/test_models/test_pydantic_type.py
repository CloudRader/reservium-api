"""Tests for `PydanticType` custom SQLAlchemy type."""

import json

from core.models.types.pydantic_type import PydanticType
from pydantic import BaseModel


# Example Pydantic model
class Rules(BaseModel):
    """The `Rules` Pydantic model."""

    night_time: bool
    max_reservation_hours: int


# Subclass for testing
class RulesType(PydanticType[Rules]):
    """Custom SQLAlchemy type for serializing and deserializing the `Rules` Pydantic model."""

    model_class = Rules


def test_python_type_property():
    """Test that the `python_type` property returns the correct Pydantic model class."""
    field = RulesType()
    assert field.python_type == Rules


def test_process_bind_param_with_model_instance():
    """Test `process_bind_param` with a Pydantic model instance."""
    rules = Rules(night_time=True, max_reservation_hours=24)
    field = RulesType()
    serialized = field.process_bind_param(rules, None)
    data = json.loads(serialized)
    assert data["night_time"] is True
    assert data["max_reservation_hours"] == 24


def test_process_bind_param_with_dict():
    """Test `process_bind_param` when given a dictionary instead of a Pydantic model."""
    rules_dict = {"night_time": False, "max_reservation_hours": 12}
    field = RulesType()
    serialized = field.process_bind_param(rules_dict, None)
    data = json.loads(serialized)
    assert data["night_time"] is False
    assert data["max_reservation_hours"] == 12


def test_process_bind_param_none():
    """Test `process_bind_param` returns None if the input is None."""
    field = RulesType()
    assert field.process_bind_param(None, None) is None


def test_process_result_value_returns_model():
    """Test `process_result_value` correctly converts a JSON string to a Pydantic model."""
    rules = Rules(night_time=True, max_reservation_hours=24)
    field = RulesType()
    json_str = json.dumps(rules.model_dump())
    result = field.process_result_value(json_str, None)
    assert isinstance(result, Rules)
    assert result.night_time is True
    assert result.max_reservation_hours == 24


def test_process_result_value_none():
    """Test `process_result_value` returns None if the database value is None."""
    field = RulesType()
    assert field.process_result_value(None, None) is None


def test_process_literal_param_with_model_instance():
    """Test `process_literal_param` with a Pydantic model instance."""
    rules = Rules(night_time=True, max_reservation_hours=24)
    field = RulesType()
    literal = field.process_literal_param(rules, None)
    data = json.loads(literal)
    assert data["night_time"] is True
    assert data["max_reservation_hours"] == 24


def test_process_literal_param_with_dict():
    """Test `process_literal_param` when given a dictionary instead of a Pydantic model."""
    rules_dict = {"night_time": False, "max_reservation_hours": 12}
    field = RulesType()
    literal = field.process_literal_param(rules_dict, None)
    data = json.loads(literal)
    assert data["night_time"] is False
    assert data["max_reservation_hours"] == 12


def test_process_literal_param_none():
    """Test `process_literal_param` returns None if the input is None."""
    field = RulesType()
    assert field.process_literal_param(None, None) is None
