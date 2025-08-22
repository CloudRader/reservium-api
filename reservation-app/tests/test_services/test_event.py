"""Module for testing email service."""

import datetime as dt

import pytest
from core.application.exceptions import BaseAppError, SoftValidationError
from core.models import EventState
from core.schemas import EventUpdate, EventUpdateTime


@pytest.mark.asyncio
async def test_post_event_not_have_this_service(
    event_create_form,
    services_data_from_is,
    user,
    calendar,
    service_event,
):
    """
    Test that posting an event fails.

    If the user doesn't have access to the required service.
    """
    with pytest.raises(SoftValidationError) as exc_info:
        await service_event.post_event(
            event_create_form,
            services_data_from_is,
            user,
            calendar,
        )
    assert str(exc_info.value) == "You don't have game service!"


@pytest.mark.asyncio
async def test_post_event_not_create_more_people_than_can_be(
    event_create_form,
    services_data_from_is,
    user,
    calendar,
    service_event,
):
    """
    Test that an event cannot be created with more guests than allowed.

    The number of guests must not exceed the limit set in the calendar configuration.
    """
    services_data_from_is[0].service.alias = "game"
    event_create_form.start_datetime = dt.datetime.now() + dt.timedelta(hours=48)
    event_create_form.end_datetime = dt.datetime.now() + dt.timedelta(hours=53)
    event_create_form.guests = 10
    calendar.more_than_max_people_with_permission = False
    with pytest.raises(SoftValidationError) as exc_info:
        await service_event.post_event(
            event_create_form,
            services_data_from_is,
            user,
            calendar,
        )
    assert str(exc_info.value) == (
        "You can't reserve this type of reservation for more than 8 people!"
    )


@pytest.mark.asyncio
async def test_post_event(
    event_create_form,
    services_data_from_is,
    user,
    calendar,
    service_event,
):
    """Test that posting an event succeeds under valid conditions."""
    services_data_from_is[0].service.alias = "game"
    event_create_form.start_datetime = dt.datetime.now() + dt.timedelta(hours=48)
    event_create_form.end_datetime = dt.datetime.now() + dt.timedelta(hours=53)
    event_body = await service_event.post_event(
        event_create_form,
        services_data_from_is,
        user,
        calendar,
    )
    assert event_body["summary"] == "Galambula"


@pytest.mark.asyncio
async def test_create_event(event, event_create_form):
    """Test creating an event."""
    assert event is not None
    assert event.purpose == event_create_form.purpose
    assert event.guests == event_create_form.guests
    assert event.reservation_start == event_create_form.start_datetime


@pytest.mark.asyncio
async def test_get_event(service_event, event):
    """Test retrieving a created event."""
    fetched_event = await service_event.get(event.id)

    assert fetched_event is not None
    assert fetched_event.id == event.id


@pytest.mark.asyncio
async def test_cancel_event(service_event, event, user):
    """Test deleting an event."""
    event.reservation_start = dt.datetime.now() + dt.timedelta(hours=1)
    event.reservation_end = dt.datetime.now() + dt.timedelta(hours=4)
    cancel_event = await service_event.cancel_event(event.id, user)

    assert cancel_event is not None
    assert cancel_event.event_state == EventState.CANCELED


@pytest.mark.asyncio
async def test_cancel_event_with_exception(service_event, event, user):
    """Test canceling an event when raise exception."""
    with pytest.raises(BaseAppError):
        await service_event.cancel_event(event.id, user)


@pytest.mark.asyncio
async def test_request_update_reservation_time(service_event, event, user):
    """Test requesting update reservation time an event."""
    event.reservation_start = dt.datetime.now() + dt.timedelta(hours=1)
    event.reservation_end = dt.datetime.now() + dt.timedelta(hours=4)
    event_update = EventUpdateTime(
        requested_reservation_start=dt.datetime.now() + dt.timedelta(hours=3),
        requested_reservation_end=dt.datetime.now() + dt.timedelta(hours=6),
    )
    request_update_reservation_time = await service_event.request_update_reservation_time(
        event.id,
        event_update,
        user,
    )

    assert request_update_reservation_time is not None
    assert request_update_reservation_time.event_state == EventState.UPDATE_REQUESTED
    assert (
        request_update_reservation_time.requested_reservation_start
        == event_update.requested_reservation_start
    )
    assert (
        request_update_reservation_time.requested_reservation_end
        == event_update.requested_reservation_end
    )


@pytest.mark.asyncio
async def test_approve_update_reservation_time(service_event, event, user):
    """Test approving update reservation time an event."""
    event.event_state = EventState.UPDATE_REQUESTED
    event_update = EventUpdate(event_state=EventState.CONFIRMED)
    approve_update_reservation_time = await service_event.approve_update_reservation_time(
        event.id,
        event_update,
        user,
    )

    assert approve_update_reservation_time is not None
    assert approve_update_reservation_time.event_state == EventState.CONFIRMED


@pytest.mark.asyncio
async def test_confirm_event(service_event, event, user):
    """Test confirming an event."""
    event.event_state = EventState.NOT_APPROVED
    confirm_event = await service_event.confirm_event(event.id, user)

    assert confirm_event is not None
    assert confirm_event.event_state == EventState.CONFIRMED


@pytest.mark.asyncio
async def test_description_of_event(service_event, user, event_create_form):
    """Test utils function in services."""
    event_create_form.additional_services = ["Bar", "Console"]
    result = service_event._description_of_event(user, event_create_form)
    assert result is not None
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_ready_event(service_event, calendar, event_create_form, user):
    """Test utils function in services."""
    result = service_event._construct_event_body(calendar, event_create_form, user)
    assert result is not None
    assert isinstance(result, dict)
    assert result["summary"] == calendar.reservation_type


@pytest.mark.asyncio
async def test_first_standard_check(services_data_from_is, reservation_service, service_event):
    """Test utils function in services."""
    start_time = dt.datetime.now() - dt.timedelta(hours=1)
    with pytest.raises(SoftValidationError) as exc_info:
        service_event._first_standard_check(
            services_data_from_is,
            reservation_service,
            start_time,
        )
    assert str(exc_info.value) == f"You don't have {reservation_service.alias} service!"

    services_data_from_is[0].service.alias = "game"
    with pytest.raises(SoftValidationError) as exc_info:
        service_event._first_standard_check(
            services_data_from_is,
            reservation_service,
            start_time,
        )
    assert str(exc_info.value) == "You can't make a reservation before the present time!"

    start_time = dt.datetime.now() + dt.timedelta(hours=5)
    service_event._first_standard_check(
        services_data_from_is,
        reservation_service,
        start_time,
    )


@pytest.mark.asyncio
async def test_control_res_in_advance(rules_schema, service_event):
    """Test utils function in services."""
    start_time = dt.datetime.now() + dt.timedelta(days=5)
    result = service_event._control_res_in_advance_or_prior(start_time, rules_schema, True)
    assert result is True
    start_time = dt.datetime.now() + dt.timedelta(days=1)
    result = service_event._control_res_in_advance_or_prior(start_time, rules_schema, True)
    assert result is False


@pytest.mark.asyncio
async def test_reservation_in_advance(rules_schema, service_event):
    """Test utils function in services."""
    start_time = dt.datetime.now() + dt.timedelta(days=1)
    with pytest.raises(SoftValidationError) as exc_info:
        service_event._reservation_in_advance(start_time, rules_schema)
    assert str(exc_info.value) == (
        f"You have to make reservations "
        f"{rules_schema.in_advance_hours} hours and "
        f"{rules_schema.in_advance_minutes} minutes in advance!"
    )

    start_time = dt.datetime.now() + dt.timedelta(days=15)
    with pytest.raises(SoftValidationError) as exc_info:
        service_event._reservation_in_advance(start_time, rules_schema)
    assert str(exc_info.value) == (
        f"You can't make reservations earlier than {rules_schema.in_prior_days} days in advance!"
    )

    start_time = dt.datetime.now() + dt.timedelta(days=7)
    service_event._reservation_in_advance(start_time, rules_schema)


@pytest.mark.asyncio
async def test_check_max_user_reservation_hours(rules_schema, service_event):
    """Test utils function in services."""
    exception = (
        f"Reservation exceeds the allowed maximum of {rules_schema.max_reservation_hours} hours."
    )
    start_time = dt.datetime.now()
    end_time = dt.datetime.now() + dt.timedelta(days=370)
    with pytest.raises(SoftValidationError) as exc_info:
        service_event._check_max_user_reservation_hours(start_time, end_time, rules_schema)
    assert str(exc_info.value) == exception
    end_time = dt.datetime.now() + dt.timedelta(days=40)
    with pytest.raises(SoftValidationError) as exc_info:
        service_event._check_max_user_reservation_hours(start_time, end_time, rules_schema)
    assert str(exc_info.value) == exception
    end_time = dt.datetime.now() + dt.timedelta(hours=33)
    with pytest.raises(SoftValidationError) as exc_info:
        service_event._check_max_user_reservation_hours(start_time, end_time, rules_schema)
    assert str(exc_info.value) == exception
    end_time = dt.datetime.now() + dt.timedelta(hours=31)
    service_event._check_max_user_reservation_hours(start_time, end_time, rules_schema)
