"""
Tests for ReservationService Pydantic Schemas
"""
from datetime import datetime, UTC
from uuid import uuid4
import pytest
from pydantic import ValidationError
from schemas.reservation_service import (
    ReservationServiceCreate,
    ReservationServiceUpdate,
    ReservationServiceInDBBase,
    ReservationService,
)

# Dummy mini service and calendar references
from schemas import MiniService, Calendar


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


def test_reservation_service_create_valid():
    """
    Test creating reservation service with valid data.
    """
    schema = ReservationServiceCreate(
        name="Projector Booking",
        alias="prjct",
        web="https://projector.com",
        contact_mail="support@projector.com",
        public=True
    )
    assert schema.name == "Projector Booking"
    assert schema.alias == "prjct"
    assert schema.web.startswith("https://")
    assert schema.contact_mail.endswith("@projector.com")
    assert schema.public is True


def test_reservation_service_create_alias_too_long():
    """
    Test that alias exceeding max length raises an error.
    """
    with pytest.raises(ValidationError):
        ReservationServiceCreate(
            name="TooLongAlias",
            alias="TOOLONG",  # more than 6 characters
        )


def test_reservation_service_update_partial():
    """
    Test partial update of reservation service.
    """
    update = ReservationServiceUpdate(
        alias="media"
    )
    assert update.alias == "media"
    assert update.name is None
    assert update.web is None
    assert update.public is None


def test_reservation_service_in_db_base_schema(valid_rules):
    """
    Test full DB representation of reservation service.
    """
    service_id = uuid4()
    now = datetime.now(UTC)
    calendar = Calendar(
        id="test_calendar@google.com",
        reservation_type="Entire Space",
        color="#00ffcc",
        max_people=10,
        more_than_max_people_with_permission=True,
        collision_with_itself=True,
        collision_with_calendar=["other_calendar_id"],
        club_member_rules=valid_rules,
        active_member_rules=valid_rules,
        manager_rules=valid_rules,
        reservation_service_id=service_id,
        mini_services=["Bar"]
    )
    mini_service = MiniService(
        id=uuid4(),
        name="Booking Help",
        reservation_service_id=service_id,
    )

    schema = ReservationServiceInDBBase(
        id=service_id,
        name="Sound System",
        alias="SOUND",
        deleted_at=now,
        calendars=[calendar],
        mini_services=[mini_service]
    )
    assert schema.id == service_id
    assert schema.name == "Sound System"
    assert schema.calendars[0].reservation_type == "Entire Space"
    assert schema.mini_services[0].name == "Booking Help"


def test_reservation_service_schema_extends_base():
    """
    Test that ReservationService schema includes all base fields.
    """
    service = ReservationService(
        id=uuid4(),
        name="Lighting",
        alias="LIGHT",
        deleted_at=None,
        calendars=[],
        mini_services=[],
    )
    assert isinstance(service, ReservationServiceInDBBase)
    assert service.deleted_at is None


@pytest.mark.parametrize("field", ["name", "alias"])
def test_reservation_service_create_required_fields(field):
    """
    Test that omitting required fields raises validation error.
    """
    data = {
        "name": "SomeName",
        "alias": "ALIAS"
    }
    del data[field]
    with pytest.raises(ValidationError):
        ReservationServiceCreate(**data)
