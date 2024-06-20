"""
Conftest for testing model
"""
import uuid
import pytest


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.fixture(scope="module")
def create_uuid():
    """
    Fixture that create uuid.
    """
    return uuid.uuid4()
