"""
Module for testing utils service
"""
import datetime as dt
import pytest

from services.utils import description_of_event, reservation_in_advance, \
    ready_event, control_res_in_advance_or_prior, dif_days_res, first_standard_check


# description_of_event, ready_event


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
def test_first_standard_check(services_data_from_is,
                              reservation_service):
    """
    Test utils function in services.
    """
    start_time = dt.datetime.now() - dt.timedelta(hours=1)
    end_time = dt.datetime.now() + dt.timedelta(hours=4)
    result = first_standard_check(services_data_from_is,
                                  reservation_service,
                                  start_time, end_time)
    assert result["message"] == f"You don't have {reservation_service.alias} service!"

    services_data_from_is[0].service.alias = "game"
    result = first_standard_check(services_data_from_is,
                                  reservation_service,
                                  start_time, end_time)
    assert result["message"] == "You can't make a reservation before the present time!"

    start_time = dt.datetime.now() + dt.timedelta(hours=5)
    result = first_standard_check(services_data_from_is,
                                  reservation_service,
                                  start_time, end_time)
    assert result["message"] == "The end of a reservation cannot be before its beginning!"

    end_time = dt.datetime.now() + dt.timedelta(hours=7)
    result = first_standard_check(services_data_from_is,
                                  reservation_service,
                                  start_time, end_time)
    assert result == "Access"


@pytest.mark.asyncio
def test_description_of_event(user,
                              event_create_form):
    """
    Test utils function in services.
    """
    event_create_form.additional_services = ["Bar", "Console"]
    result = description_of_event(user,
                                  event_create_form)
    assert result is not None
    assert isinstance(result, str)


@pytest.mark.asyncio
def test_ready_event(calendar,
                     event_create_form,
                     user):
    """
    Test utils function in services.
    """
    result = ready_event(calendar, event_create_form, user)
    assert result is not None
    assert isinstance(result, dict)
    assert result["summary"] == calendar.reservation_type


@pytest.mark.asyncio
def test_control_res_in_advance(rules_schema):
    """
    Test utils function in services.
    """
    start_time = dt.datetime.now() + dt.timedelta(days=5)
    result = control_res_in_advance_or_prior(start_time, rules_schema, True)
    assert result is True
    start_time = dt.datetime.now() + dt.timedelta(days=1)
    result = control_res_in_advance_or_prior(start_time, rules_schema, True)
    assert result is False


@pytest.mark.asyncio
def test_reservation_in_advance(rules_schema):
    """
    Test utils function in services.
    """
    start_time = dt.datetime.now() + dt.timedelta(days=1)
    result = reservation_in_advance(start_time, rules_schema)
    assert result["message"] == (f"You have to make reservations "
                                 f"{rules_schema.in_advance_hours} hours and "
                                 f"{rules_schema.in_advance_minutes} minutes in advance!")

    start_time = dt.datetime.now() + dt.timedelta(days=15)
    result = reservation_in_advance(start_time, rules_schema)
    assert result["message"] == (f"You can't make reservations earlier than "
                                 f"{rules_schema.in_prior_days} days "
                                 f"in advance!")

    start_time = dt.datetime.now() + dt.timedelta(days=7)
    result = reservation_in_advance(start_time, rules_schema)
    assert result == "Access"


@pytest.mark.asyncio
def test_dif_days_res(rules_schema):
    """
    Test utils function in services.
    """
    start_time = dt.datetime.now()
    end_time = dt.datetime.now() + dt.timedelta(days=370)
    result = dif_days_res(start_time, end_time, rules_schema)
    assert result is False
    end_time = dt.datetime.now() + dt.timedelta(days=40)
    result = dif_days_res(start_time, end_time, rules_schema)
    assert result is False
    end_time = dt.datetime.now() + dt.timedelta(hours=33)
    result = dif_days_res(start_time, end_time, rules_schema)
    assert result is False
    end_time = dt.datetime.now() + dt.timedelta(hours=31)
    result = dif_days_res(start_time, end_time, rules_schema)
    assert result is True
