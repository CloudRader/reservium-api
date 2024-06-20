"""
Module for testing mini service schema
"""
import uuid
import pytest

from schemas import User


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.fixture(scope="module")
def user_schema() -> User:
    """
    Fixture that return mini service schema.
    """
    return User(
        uuid=uuid.uuid4(),
        username="klapdamrap",
        user_token="h,gmmhuk;ohkulmh",
        active_member=True,
        roles=["Baka", "Laka", "MAKA"],
    )


def test_conversion_to_dict(user_schema):
    """
    Check if rules is correctly converted to dictionary.

    :param user_schema: User schema.
    """
    res_dict = user_schema.model_dump()

    assert res_dict["uuid"] == user_schema.uuid
    assert res_dict["username"] == user_schema.username
    assert res_dict["user_token"] == user_schema.user_token
    assert res_dict["active_member"] == user_schema.active_member
    assert res_dict["roles"] == user_schema.roles
