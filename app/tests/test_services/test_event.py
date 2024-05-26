"""
Module for testing event service.
"""
from services import EventService

import pytest


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest

@pytest.fixture()
def service_event(db_session) -> EventService:
    """
    Return EventService.
    """
    return EventService(db=db_session)


def test_created_calendar(service_calendar, calendar_create):
    """
    Creating calendar in tmp db for passing next test.
    """
    service_calendar.create(calendar_create)


def test_post_event(create_user_manager_stud, service_event,
                    event_create, information_data_from_is):
    """
    Test posting event to google calendar.
    To avoid communication with Google calendar API in tests,
    the test reaches the last check and fails it.
    """
    creds = None
    event = service_event.post_event(
        event_create, information_data_from_is,
        create_user_manager_stud, creds
    )
    assert event is not None
    assert event["message"] == \
           "You can't make reservations at night!"
