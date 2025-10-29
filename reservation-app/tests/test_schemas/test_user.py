"""Tests for UserLite Pydantic Schemas."""

from datetime import datetime

import pytest
from core.schemas.user import UserCreate, UserLite, UserUpdate
from pydantic import ValidationError


def test_user_create_schema_valid():
    """Test creating a user with valid data."""
    schema = UserCreate(
        id=2142,
        username="TestUser",
        full_name="Gars Lars",
        active_member=True,
        section_head=False,
        roles=["Bar", "Consoles"],
    )
    assert schema.id == 2142
    assert schema.username == "TestUser"
    assert schema.active_member is True
    assert schema.section_head is False
    assert {"Bar", "Consoles"} <= set(schema.roles)


def test_user_create_schema_invalid_roles_type():
    """Test that invalid role type raises an error."""
    with pytest.raises(ValidationError):
        UserCreate(
            id=2142,
            username="TestUser",
            full_name="Gars Lars",
            active_member=True,
            section_head=False,
            roles="Admin",  # Should be a list, not string
        )


def test_user_update_partial_schema():
    """Test updating user with partial data."""
    update = UserUpdate(username="UpdatedName")
    assert update.username == "UpdatedName"
    assert update.active_member is None
    assert update.section_head is None
    assert update.roles is None


def test_user_in_db_base_schema():
    """Test full user DB representation."""
    user = UserLite(
        id=42,
        username="TestUser",
        full_name="Gars Lars",
        active_member=False,
        section_head=True,
        deleted_at=None,
        roles=["Bar"],
    )
    assert user.id == 42
    assert user.deleted_at is None
    assert user.roles == ["Bar"]


def test_user_schema_extends_base():
    """Test that UserLite schema includes all base fields."""
    now = datetime.now()
    user = UserLite(
        id=1,
        username="TestUser",
        full_name="Gars Lars",
        active_member=True,
        section_head=False,
        deleted_at=now,
        roles=["Tech"],
    )
    assert isinstance(user, UserLite)
    assert user.deleted_at == now


@pytest.mark.parametrize("field", ["id", "username", "active_member", "section_head"])
def test_user_create_required_fields(field):
    """Test that omitting required fields raises validation error."""
    data = {
        "id": 1,
        "username": "Test",
        "full_name": "Gars Lars",
        "room_number": "212",
        "active_member": True,
        "section_head": False,
        "roles": ["Tech"],
    }
    del data[field]
    with pytest.raises(ValidationError):
        UserCreate(**data)
