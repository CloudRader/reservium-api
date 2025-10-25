"""Tests for MiniServiceDetail Pydantic Schemas."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from core.schemas.mini_service import (
    MiniServiceCreate,
    MiniServiceDetail,
    MiniServiceLite,
    MiniServiceUpdate,
)
from pydantic import ValidationError


def test_mini_service_create_valid():
    """Test creating a mini service with valid data."""
    service_id = uuid4().hex
    schema = MiniServiceCreate(reservation_service_id=service_id, name="Media Setup")
    assert schema.name == "Media Setup"
    assert schema.reservation_service_id == service_id


def test_mini_service_update_partial():
    """Test updating mini service with partial data."""
    update = MiniServiceUpdate(name="New Name")
    assert update.name == "New Name"


def test_mini_service_in_db_base_schema():
    """Test full mini service DB representation."""
    service_id = uuid4().hex
    mini_id = uuid4().hex
    now = datetime.now(UTC)

    schema = MiniServiceLite(
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
    """Test that MiniServiceDetail schema includes all base fields."""
    schema = MiniServiceDetail(
        id=uuid4().hex,
        reservation_service_id=uuid4().hex,
        name="3D Printer",
        deleted_at=None,
    )
    assert isinstance(schema, MiniServiceLite)
    assert schema.name == "3D Printer"
    assert schema.deleted_at is None


@pytest.mark.parametrize("field", ["name", "reservation_service_id"])
def test_mini_service_create_required_fields(field):
    """Test that omitting required fields raises validation error."""
    data = {
        "name": "Basic MiniServiceDetail",
        "reservation_service_id": uuid4(),
    }
    del data[field]
    with pytest.raises(ValidationError):
        MiniServiceCreate(**data)
