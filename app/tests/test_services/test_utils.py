"""
Module for testing utils service
"""
import pytest
# from models import CalendarModel
from services.utils import service_availability_check
                            # description_of_event, ready_event


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_service_availability_check(services_data_from_is):
    """
    Test utils function in services.
    """
    # Case where the service is available
    result = service_availability_check(services_data_from_is, "stud")
    assert result is True

    # Case where the service is not available
    result = service_availability_check(services_data_from_is, "club")
    assert result is False


# def test_description_of_event(mock_information, mock_event_input):
#     result = description_of_event(mock_information.user, mock_information.room, mock_event_input)
#     assert "Name: John Doe" in result
#     assert "Room: 101" in result
#     assert "Participants: 10" in result
#     assert "Purpose: Meeting" in result
#     assert "Additionals: Wi-Fi" in result
#
#
# def test_ready_event(mock_event_input, mock_information):
#     calendar = CalendarModel(reservation_type="Meeting Room")
#     event_body = ready_event(calendar, mock_event_input, mock_information)
#
#     assert event_body["summary"] == "Meeting Room"
#     assert "Name: John Doe Doe" in event_body["description"]
#     assert event_body["start"]["timeZone"] == "Europe/Prague"
#     assert event_body["end"]["timeZone"] == "Europe/Prague"
#     assert event_body["attendees"][0]["email"] == mock_event_input.email
