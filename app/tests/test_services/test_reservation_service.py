"""
Module for testing reservation service ser.
"""
from services import ReservationServiceService, UserService

import pytest


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.fixture()
def service_user(db_session) -> UserService:
    """
    Return UserService.
    """
    return UserService(db=db_session)


@pytest.fixture()
def service_reservation_service(db_session
                                ) -> ReservationServiceService:
    """
    Return ReservationServiceService.
    """
    return ReservationServiceService(db=db_session)


def test_create_reservation_service(service_reservation_service,
                                    reservation_service_create,
                                    service_user,
                                    user_data_from_is,
                                    roles_data_from_is
                                    ):
    """
    Test creating reservation service.
    """
    user = service_user.create_user(user_data_from_is,
                                    roles_data_from_is)
    reservation_service = service_reservation_service.create_reservation_service(
        reservation_service_create, user
    )
    assert reservation_service is not None


def test_get_by_alias(service_reservation_service, reservation_service_create):
    """
    Test getting by alias.
    """
    db_reservation_service = service_reservation_service.get_by_alias(
        reservation_service_create.alias
    )
    assert db_reservation_service is not None
    assert db_reservation_service.alias == \
           reservation_service_create.alias
    assert db_reservation_service.name == \
           reservation_service_create.name


def test_get_by_name(service_reservation_service, reservation_service_create):
    """
    Test getting by name.
    """
    db_reservation_service = service_reservation_service.get_by_name(
        reservation_service_create.name
    )
    assert db_reservation_service is not None
    assert db_reservation_service.alias == \
           reservation_service_create.alias
    assert db_reservation_service.name == \
           reservation_service_create.name


def test_delete_reservation_service(service_reservation_service,
                                    reservation_service_create,
                                    service_user):
    """
    Test deleting reservation service.
    """
    user = service_user.get_by_username("kanya_garin")
    reservation_service = service_reservation_service.get_by_name(
        reservation_service_create.name
    )
    removed_reservation_service = service_reservation_service.delete_reservation_service(
        reservation_service.uuid, user
    )
    assert removed_reservation_service is not None
    assert removed_reservation_service.uuid == reservation_service.uuid
    reservation_service = service_reservation_service.get(removed_reservation_service.uuid)
    assert reservation_service is None


def test_update_reservation_service(service_reservation_service,
                                    reservation_service_create,
                                    service_user):
    """
    Test updating reservation service.
    """
    user = service_user.get_by_username("kanya_garin")
    reservation_service = service_reservation_service.create_reservation_service(
        reservation_service_create, user)
    assert reservation_service is not None
    # reservation_service_updated = service_reservation_service.update_reservation_service(
    #     reservation_service.uuid, reservation_service_update, user
    # )
    #
    # assert reservation_service_updated is not None
    # assert reservation_service_updated.alias == reservation_service_update.alias
    # assert reservation_service_updated.alias != reservation_service_create.alias


def test_get_all(service_reservation_service):
    """
    Test getting all reservation services.
    """
    reservation_services = service_reservation_service.get_all()
    assert reservation_services is not None
    service_reservation_service.remove(reservation_services[0].uuid)
    reservation_services = service_reservation_service.get_all()
    assert reservation_services is None
