"""
This module provides fixtures for test services
"""
import pytest
from services import ReservationServiceService, UserService, \
    MiniServiceService


# Using fixtures as variables is a standard for pytest
# pylint: disable=redefined-outer-name


@pytest.fixture()
def service_user(db_session) -> UserService:
    """
    Return UserService.
    """
    return UserService(db=db_session)


@pytest.fixture()
def service_reservation_service(db_session) -> ReservationServiceService:
    """
    Return ReservationServiceService.
    """
    return ReservationServiceService(db=db_session)


@pytest.fixture()
def service_mini_service(db_session) -> MiniServiceService:
    """
    Return MiniServiceService.
    """
    return MiniServiceService(db=db_session)
