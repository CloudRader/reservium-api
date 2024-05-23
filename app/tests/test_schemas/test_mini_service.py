"""
Module for testing mini service schema
"""
import uuid
import pytest

from schemas import MiniService


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.fixture(scope="module")
def mini_service_schema() -> MiniService:
    """
    Fixture that return mini service schema.
    """
    return MiniService(
        uuid=uuid.uuid4(),
        name="Board games",
        service_alias="something other"
    )


def test_conversion_to_dict(mini_service_schema):
    """
    Check if rules is correctly converted to dictionary.

    :param mini_service_schema: Mini Service schema.
    """
    res_dict = mini_service_schema.model_dump()

    assert res_dict["uuid"] == mini_service_schema.uuid
    assert res_dict["name"] == mini_service_schema.name
    assert res_dict["service_alias"] == mini_service_schema.service_alias
