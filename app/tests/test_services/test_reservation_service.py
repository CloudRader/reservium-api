"""
Module for testing reservation service ser.
"""


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


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


def test_get_after_soft_delete(service_reservation_service, reservation_service_create,
                               service_user):
    """
    Test soft delete and getting soft delete object.
    """
    user = service_user.get_by_username("kanya_garin")
    db_reservation_service = service_reservation_service.get_by_alias(
        reservation_service_create.alias
    )
    deleted = service_reservation_service.delete_reservation_service(db_reservation_service.id,
                                                                     user)
    get_reservation_service = service_reservation_service.get(deleted.id)
    assert get_reservation_service is None
    soft_deleted_reservation_service = service_reservation_service.get(deleted.id, True)
    assert soft_deleted_reservation_service is not None


def test_delete_reservation_service(service_reservation_service,
                                    reservation_service_create):
    """
    Test deleting reservation service.
    """
    reservation_service = service_reservation_service.get_by_name(
        reservation_service_create.name, True
    )
    removed_reservation_service = service_reservation_service.remove(
        reservation_service.id
    )
    assert removed_reservation_service is not None
    assert removed_reservation_service.id == reservation_service.id
    reservation_service = service_reservation_service.get(removed_reservation_service.id)
    assert reservation_service is None


def test_update_reservation_service(service_reservation_service,
                                    reservation_service_create,
                                    service_user, reservation_service_update):
    """
    Test updating reservation service.
    """
    user = service_user.get_by_username("kanya_garin")
    reservation_service = service_reservation_service.create_reservation_service(
        reservation_service_create, user)
    assert reservation_service is not None
    reservation_service_updated = service_reservation_service.update_reservation_service(
        reservation_service.id, reservation_service_update, user
    )

    assert reservation_service_updated is not None
    assert reservation_service_updated.web == "something"


def test_get_all(service_reservation_service):
    """
    Test getting all reservation services.
    """
    reservation_services = service_reservation_service.get_all()
    assert reservation_services is not None
    service_reservation_service.remove(reservation_services[0].id)
    reservation_services = service_reservation_service.get_all()
    assert reservation_services is None
