"""
Module for testing calendar schema
"""
import pytest

from schemas import Rules, Calendar


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest

@pytest.fixture(scope="module")
def rules_schema() -> Rules:
    """
    Fixture that return rules schema.
    """
    return Rules(
        night_time=False,
        reservation_more_24_hours=False,
        in_advance_hours=24,
        in_advance_minutes=30,
        in_advance_day=14,
    )


@pytest.fixture(scope="module")
def calendar_schema(rules_schema) -> Calendar:
    """
    Fixture that return calendar schema.
    """
    return Calendar(
        calendar_id="c_f8a87bad9df63841a343835e6c55964349",
        service_alias="klub",
        reservation_type="Table Soccer",
        event_name="Stolní Fotbal/Table Soccer",
        max_people=6,
        collision_with_itself=False,
        club_member_rules=rules_schema,
        active_member_rules=rules_schema,
        manager_rules=rules_schema,
        mini_services=["Pool", "Something else"]
    )


def test_conversion_to_dict(calendar_schema):
    """
    Check if rules is correctly converted to dictionary.

    :param calendar_schema: Calendar schema.
    """
    res_dict = calendar_schema.model_dump()

    assert res_dict["calendar_id"] == calendar_schema.calendar_id
    assert res_dict["service_alias"] == calendar_schema.service_alias
    assert res_dict["reservation_type"] == calendar_schema.reservation_type
    assert res_dict["event_name"] == calendar_schema.event_name
    assert res_dict["max_people"] == calendar_schema.max_people
    assert res_dict["collision_with_itself"] == calendar_schema.collision_with_itself
    assert res_dict["mini_services"] == calendar_schema.mini_services
