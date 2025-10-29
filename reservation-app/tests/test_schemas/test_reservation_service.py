"""Tests for ReservationServiceDetail Pydantic Schemas."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

# Dummy mini service and calendar references
from core.schemas import CalendarDetail, MiniServiceDetail
from core.schemas.reservation_service import (
    ReservationServiceCreate,
    ReservationServiceDetail,
    ReservationServiceLite,
    ReservationServiceUpdate,
)
from pydantic import ValidationError


def test_reservation_service_create_valid():
    """Test creating reservation service with valid data."""
    schema = ReservationServiceCreate(
        name="Projector Booking",
        alias="prjct",
        web="https://projector.com",
        contact_mail="support@projector.com",
        public=True,
    )
    assert schema.name == "Projector Booking"
    assert schema.alias == "prjct"
    assert schema.web.startswith("https://")
    assert schema.contact_mail.endswith("@projector.com")
    assert schema.public is True


def test_reservation_service_create_alias_too_long():
    """Test that alias exceeding max length raises an error."""
    with pytest.raises(ValidationError):
        ReservationServiceCreate(
            name="TooLongAlias",
            alias="TOOLONG",  # more than 6 characters
        )


def test_reservation_service_update_partial():
    """Test partial update of reservation service."""
    update = ReservationServiceUpdate(alias="media")
    assert update.alias == "media"
    assert update.name is None
    assert update.web is None
    assert update.public is None


def test_reservation_service_in_db_base_schema(valid_rules):
    """Test full DB representation of reservation service."""
    service_id = uuid4().hex
    now = datetime.now(UTC)
    calendar = CalendarDetail(
        id="test_calendar@google.com",
        reservation_type="Entire Space",
        color="#00ffcc",
        max_people=10,
        more_than_max_people_with_permission=True,
        collision_with_itself=True,
        club_member_rules=valid_rules,
        active_member_rules=valid_rules,
        manager_rules=valid_rules,
        reservation_service_id=service_id,
    )
    mini_service = MiniServiceDetail(
        id=uuid4().hex,
        name="Booking Help",
        reservation_service_id=service_id,
    )

    schema_in_db_base = ReservationServiceLite(
        id=service_id,
        name="Sound System",
        alias="SOUND",
        deleted_at=now,
    )
    schema = ReservationServiceDetail(
        id=service_id,
        name="Sound System",
        alias="SOUND",
        calendars=[calendar],
        mini_services=[mini_service],
    )
    assert schema_in_db_base.id == service_id
    assert schema_in_db_base.name == "Sound System"
    assert schema.calendars[0].reservation_type == "Entire Space"
    assert schema.mini_services[0].name == "Booking Help"


def test_reservation_service_schema_extends_base():
    """Test that ReservationServiceDetail schema includes all base fields."""
    service = ReservationServiceDetail(
        id=uuid4().hex,
        name="Lighting",
        alias="LIGHT",
        deleted_at=None,
        calendars=[],
        mini_services=[],
    )
    assert isinstance(service, ReservationServiceLite)
    assert service.deleted_at is None


@pytest.mark.parametrize("field", ["name", "alias"])
def test_reservation_service_create_required_fields(field):
    """Test that omitting required fields raises validation error."""
    data = {"name": "SomeName", "alias": "ALIAS"}
    del data[field]
    with pytest.raises(ValidationError):
        ReservationServiceCreate(**data)
