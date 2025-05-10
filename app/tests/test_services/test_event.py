"""
Module for testing email service.
"""
import datetime as dt
import pytest


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_post_event_not_have_this_service(event_create_form,
                                                services_data_from_is,
                                                user,
                                                calendar,
                                                service_event):
    """
    Test that posting an event fails if the user doesn't have
    access to the required service.
    """
    result = await service_event.post_event(event_create_form,
                                            services_data_from_is,
                                            user,
                                            calendar)
    assert result["message"] == "You don't have game service!"


@pytest.mark.asyncio
async def test_post_event_with_not_exist_reservation_type(
        event_create_form, services_data_from_is, user, service_event
):
    """
    Test that posting an event fails if the calendar type does not exist.
    """
    result = await service_event.post_event(event_create_form,
                                            services_data_from_is,
                                            user,
                                            None)
    assert result["message"] == "Calendar with that type not exist!"


@pytest.mark.asyncio
async def test_post_event_not_create_more_people_than_can_be(
        event_create_form, services_data_from_is, user,
        calendar, service_event
):
    """
    Test that an event cannot be created with more guests
    than allowed by the calendar configuration.
    """
    services_data_from_is[0].service.alias = "game"
    event_create_form.start_datetime = dt.datetime.now() + dt.timedelta(hours=48)
    event_create_form.end_datetime = dt.datetime.now() + dt.timedelta(hours=53)
    event_create_form.guests = 10
    calendar.more_than_max_people_with_permission = False
    result = await service_event.post_event(event_create_form,
                                            services_data_from_is,
                                            user,
                                            calendar)
    assert result["message"] == ("You can't reserve this type of "
                                 "reservation for more than 8 people!")


@pytest.mark.asyncio
async def test_post_event(event_create_form,
                          services_data_from_is,
                          user,
                          calendar,
                          service_event):
    """
    Test that posting an event succeeds under valid conditions.
    """
    services_data_from_is[0].service.alias = "game"
    event_create_form.start_datetime = dt.datetime.now() + dt.timedelta(hours=48)
    event_create_form.end_datetime = dt.datetime.now() + dt.timedelta(hours=53)
    event_body = await service_event.post_event(event_create_form,
                                                services_data_from_is,
                                                user,
                                                calendar)
    assert not (len(event_body) == 1 and 'message' in event_body)
