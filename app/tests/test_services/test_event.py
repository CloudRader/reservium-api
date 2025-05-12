"""
Module for testing email service.
"""
import datetime as dt
import pytest

from models import EventState
from api import BaseAppException
from schemas import EventUpdate


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


@pytest.mark.asyncio
async def test_create_event(event, event_create_form):
    """
    Test creating an event.
    """
    assert event is not None
    assert event.purpose == event_create_form.purpose
    assert event.guests == event_create_form.guests
    assert event.start_datetime == event_create_form.start_datetime


@pytest.mark.asyncio
async def test_get_event(service_event, event):
    """
    Test retrieving a created event.
    """
    fetched_event = await service_event.get(event.id)

    assert fetched_event is not None
    assert fetched_event.id == event.id


@pytest.mark.asyncio
async def test_cancel_event(service_event, event, user):
    """
    Test deleting an event.
    """
    event.start_datetime = dt.datetime.now() + dt.timedelta(hours=1)
    event.end_datetime = dt.datetime.now() + dt.timedelta(hours=4)
    cancel_event = await service_event.cancel_event(event.id, user)

    assert cancel_event is not None
    assert cancel_event.event_state == EventState.CANCELED


@pytest.mark.asyncio
async def test_cancel_event_with_exception(service_event, event, user):
    """
    Test canceling an event when raise exception.
    """
    with pytest.raises(BaseAppException):
        await service_event.cancel_event(
            event.id, user
        )


@pytest.mark.asyncio
async def test_request_update_reservation_time(service_event, event, user):
    """
    Test requesting update reservation time an event.
    """
    event.start_datetime = dt.datetime.now() + dt.timedelta(hours=1)
    event.end_datetime = dt.datetime.now() + dt.timedelta(hours=4)
    event_update = EventUpdate(
        start_datetime=dt.datetime.now() + dt.timedelta(hours=3),
        end_datetime=dt.datetime.now() + dt.timedelta(hours=6)
    )
    request_update_reservation_time = await service_event.request_update_reservation_time(
        event.id, event_update, user
    )

    assert request_update_reservation_time is not None
    assert request_update_reservation_time.event_state == EventState.UPDATE_REQUESTED
    assert request_update_reservation_time.start_datetime == event_update.start_datetime
    assert request_update_reservation_time.end_datetime == event_update.end_datetime


@pytest.mark.asyncio
async def test_approve_update_reservation_time(service_event, event, user):
    """
    Test approving update reservation time an event.
    """
    event.event_state = EventState.UPDATE_REQUESTED
    event_update = EventUpdate(
        event_state=EventState.CONFIRMED
    )
    approve_update_reservation_time = await service_event.approve_update_reservation_time(
        event.id, event_update, user
    )

    assert approve_update_reservation_time is not None
    assert approve_update_reservation_time.event_state == EventState.CONFIRMED


@pytest.mark.asyncio
async def test_confirm_event(service_event, event, user):
    """
    Test confirming an event.
    """
    event.event_state = EventState.NOT_APPROVED
    confirm_event = await service_event.confirm_event(event.id, user)

    assert confirm_event is not None
    assert confirm_event.event_state == EventState.CONFIRMED
