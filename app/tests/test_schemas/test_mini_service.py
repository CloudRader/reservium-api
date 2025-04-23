"""
Tests for MiniService Pydantic Schemas
"""
from datetime import datetime, UTC
from uuid import uuid4
import pytest
from pydantic import ValidationError
from schemas.mini_service import (
    MiniServiceCreate,
    MiniServiceUpdate,
    MiniServiceInDBBase,
    MiniService,
)


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


def test_mini_service_create_valid():
    """
    Test creating a mini service with valid data.
    """
    service_id = uuid4()
    schema = MiniServiceCreate(
        reservation_service_id=service_id,
        name="Media Setup"
    )
    assert schema.name == "Media Setup"
    assert schema.reservation_service_id == service_id


def test_mini_service_update_partial():
    """
    Test updating mini service with partial data.
    """
    update = MiniServiceUpdate(name="New Name")
    assert update.name == "New Name"


def test_mini_service_in_db_base_schema():
    """
    Test full mini service DB representation.
    """
    service_id = uuid4()
    mini_id = uuid4()
    now = datetime.now(UTC)

    schema = MiniServiceInDBBase(
        id=mini_id,
        reservation_service_id=service_id,
        name="Print Station",
        deleted_at=now,
    )

    assert schema.id == mini_id
    assert schema.name == "Print Station"
    assert schema.reservation_service_id == service_id
    assert schema.deleted_at == now


def test_mini_service_schema_extends_base():
    """
    Test that MiniService schema includes all base fields.
    """
    schema = MiniService(
        id=uuid4(),
        reservation_service_id=uuid4(),
        name="3D Printer",
        deleted_at=None,
    )
    assert isinstance(schema, MiniServiceInDBBase)
    assert schema.name == "3D Printer"
    assert schema.deleted_at is None


@pytest.mark.parametrize("field", ["name", "reservation_service_id"])
def test_mini_service_create_required_fields(field):
    """
    Test that omitting required fields raises validation error.
    """
    data = {
        "name": "Basic MiniService",
        "reservation_service_id": uuid4(),
    }
    del data[field]
    with pytest.raises(ValidationError):
        MiniServiceCreate(**data)
