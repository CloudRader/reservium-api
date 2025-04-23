"""
Tests for Calendar Pydantic Schemas
"""
from datetime import datetime, UTC
from uuid import uuid4
import pytest
from pydantic import ValidationError
from schemas.calendar import (
    Rules,
    CalendarCreate,
    CalendarUpdate,
    CalendarInDBBase,
    Calendar,
)


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


def test_calendar_create_valid(valid_rules):
    """
    Test creating a calendar with valid data.
    """
    schema = CalendarCreate(
        reservation_service_id=uuid4(),
        reservation_type="Event",
        max_people=25,
        collision_with_itself=True,
        club_member_rules=valid_rules,
        active_member_rules=valid_rules,
        manager_rules=valid_rules,
        id="calendar1",
        collision_with_calendar=["calendar2"],
        more_than_max_people_with_permission=False,
        mini_services=["printer", "scanner"],
        color="#FF0000"
    )
    assert schema.reservation_type == "Event"
    assert schema.max_people == 25
    assert schema.club_member_rules.max_reservation_hours == 4
    assert "scanner" in schema.mini_services
    assert "calendar2" in schema.collision_with_calendar


def test_calendar_create_invalid_max_people(valid_rules):
    """
    Test that calendar creation fails when max_people is below 1.
    """
    with pytest.raises(ValidationError):
        CalendarCreate(
            reservation_service_id=uuid4(),
            reservation_type="Workshop",
            max_people=0,
            collision_with_itself=True,
            club_member_rules=valid_rules,
            active_member_rules=valid_rules,
            manager_rules=valid_rules,
        )


def test_calendar_update_partial():
    """
    Test updating calendar with partial fields.
    """
    update = CalendarUpdate(
        reservation_type="Meeting",
        max_people=15,
        collision_with_itself=False,
        mini_services=["projector"]
    )
    assert update.reservation_type == "Meeting"
    assert update.max_people == 15
    assert update.collision_with_itself is False
    assert update.mini_services == ["projector"]


def test_calendar_in_db_schema(valid_rules):
    """
    Test full calendar DB schema with all fields.
    """
    now = datetime.now(UTC)
    schema = CalendarInDBBase(
        id="calendar123",
        deleted_at=now,
        reservation_type="Presentation",
        max_people=50,
        collision_with_itself=False,
        club_member_rules=valid_rules,
        active_member_rules=valid_rules,
        manager_rules=valid_rules,
        reservation_service_id=uuid4(),
        mini_services=["TV"],
        color="#00FF00"
    )
    assert schema.id == "calendar123"
    assert schema.deleted_at == now
    assert schema.color == "#00FF00"
    assert schema.club_member_rules.in_prior_days == 7


def test_calendar_schema_extends_base(valid_rules):
    """
    Test that Calendar schema extends base schema correctly.
    """
    calendar = Calendar(
        id="calendarABC",
        deleted_at=None,
        reservation_type="Training",
        max_people=10,
        collision_with_itself=True,
        club_member_rules=valid_rules,
        active_member_rules=valid_rules,
        manager_rules=valid_rules,
        reservation_service_id=uuid4(),
    )
    assert isinstance(calendar, CalendarInDBBase)
    assert calendar.reservation_type == "Training"


@pytest.mark.parametrize("field", ["reservation_type",
                                   "max_people",
                                   "collision_with_itself",
                                   "club_member_rules"])
def test_calendar_create_required_fields(field, valid_rules):
    """
    Test that missing required fields raises a validation error.
    """
    data = {
        "reservation_service_id": uuid4(),
        "reservation_type": "Talk",
        "max_people": 20,
        "collision_with_itself": True,
        "club_member_rules": valid_rules,
        "active_member_rules": valid_rules,
        "manager_rules": valid_rules,
    }
    del data[field]
    with pytest.raises(ValidationError):
        CalendarCreate(**data)


def test_rules_field_validation():
    """
    Test invalid values for fields inside Rules.
    """
    with pytest.raises(ValidationError):
        Rules(
            night_time=True,
            reservation_without_permission=True,
            max_reservation_hours=-1,  # Invalid
            in_advance_hours=1,
            in_advance_minutes=0,
            in_prior_days=0
        )
