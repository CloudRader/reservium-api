"""
Module for testing mini service ser.
"""
from services import MiniServiceService

import pytest


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.fixture()
def service_mini_service(db_session) -> MiniServiceService:
    """
    Return MiniServiceService.
    """
    return MiniServiceService(db=db_session)


def test_create_mini_service(service_mini_service, mini_service_create,
                             service_user, user_data_from_is,
                             roles_data_from_is):
    """
    Test creating mini service.
    """
    user = service_user.create_user(user_data_from_is,
                                    roles_data_from_is,
                                    "fhailwt7taf")
    mini_service = service_mini_service.create_mini_service(
        mini_service_create, user
    )
    assert mini_service is not None


def test_get_by_service_alias(service_mini_service, mini_service_create):
    """
    Test getting by service alias.
    """
    db_mini_services = service_mini_service.get_by_service_alias(
        mini_service_create.service_alias
    )
    assert db_mini_services is not None
    assert db_mini_services[0].service_alias == \
           mini_service_create.service_alias
    assert db_mini_services[0].name == \
           mini_service_create.name


def test_get_by_name(service_mini_service, mini_service_create):
    """
    Test getting by service name.
    """
    db_mini_service = service_mini_service.get_by_name(
        mini_service_create.name
    )
    assert db_mini_service is not None


def test_delete_mini_service(service_mini_service, mini_service_create,
                             service_user):
    """
    Test deleting mini service.
    """
    user = service_user.get_by_token("fhailwt7taf")
    mini_service = service_mini_service.get_by_name(
        mini_service_create.name
    )
    removed_mini_service = service_mini_service.delete_mini_service(
        mini_service.uuid, user
    )
    assert removed_mini_service is not None
    assert removed_mini_service.uuid == mini_service.uuid
    mini_service = service_mini_service.get(removed_mini_service.uuid)
    assert mini_service is None


def test_remove_nonexistent_mini_service(service_mini_service, mini_service_create):
    """
    Test deleting nonexistent calendar.
    """
    mini_service = service_mini_service.create(mini_service_create)
    mini_service_removed = service_mini_service.remove(mini_service.uuid)
    assert mini_service_removed is not None
    mini_service_removed = service_mini_service.remove(mini_service_removed.uuid)
    assert mini_service_removed is None
    mini_service_removed = service_mini_service.remove(None)
    assert mini_service_removed is None


def test_update_mini_service(service_mini_service, mini_service_create,
                             mini_service_update, service_user):
    """
    Test updating mini service.
    """
    user = service_user.get_by_token("fhailwt7taf")
    mini_service = service_mini_service.create_mini_service(mini_service_create, user)
    mini_service_updated = service_mini_service.update_mini_service(
        mini_service.uuid, mini_service_update, user
    )

    assert mini_service_updated is not None
    assert mini_service_updated.service_alias == mini_service_update.service_alias


def test_get_all(service_mini_service):
    """
    Test getting all mini services.
    """
    mini_services = service_mini_service.get_all()
    assert mini_services is not None
    service_mini_service.remove(mini_services[0].uuid)
    calendars = service_mini_service.get_all()
    assert calendars is None
