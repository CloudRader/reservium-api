"""
Module for testing document service.
"""


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


def test_create_calendar(service_calendar, calendar_create,
                         service_user, user_data_from_is,
                         roles_data_from_is):
    """
    Test creating calendar.
    """
    user = service_user.create_user(user_data_from_is,
                                    roles_data_from_is,
                                    "fkbwa;uwfgagflwy")
    calendar = service_calendar.create_calendar(calendar_create, user)
    assert calendar is not None


def test_get_by_calendar_id(service_calendar, calendar_create):
    """
    Test getting created calendar.
    """
    db_calendar = service_calendar.get_by_calendar_id(calendar_create.calendar_id)
    assert db_calendar is not None


def test_get_by_service_alias(service_calendar, calendar_create):
    """
    Test getting by service alias.
    """
    db_calendar = service_calendar.get_by_service_alias(calendar_create.service_alias)
    assert db_calendar is not None


def test_get_mini_services_by_reservation_type(
        service_calendar, calendar_create):
    """
    Test getting mini services by reservation type.
    """
    mini_services = service_calendar.get_mini_services_by_reservation_type(
        calendar_create.reservation_type
    )
    assert mini_services is not None
    assert mini_services[0] == "Bar"
    assert mini_services[1] == "Consoles"
    assert mini_services[2] == "Games"


def test_delete_calendar(service_calendar, calendar_create,
                         service_user):
    """
    Test deleting calendar.
    """
    user = service_user.get_by_token("fkbwa;uwfgagflwy")
    removed_calendar = service_calendar.delete_calendar(
        calendar_create.calendar_id,
        user
    )
    assert removed_calendar is not None
    assert removed_calendar.calendar_id == calendar_create.calendar_id
    db_calendar = service_calendar.get(removed_calendar.calendar_id)
    assert db_calendar is None


def test_remove_nonexistent_calendar(service_calendar, calendar_create):
    """
    Test deleting nonexistent calendar.
    """
    calendar = service_calendar.create(calendar_create)
    calendar_removed = service_calendar.remove(calendar.calendar_id)
    assert calendar_removed is not None
    calendar_removed = service_calendar.remove(calendar_removed.calendar_id)
    assert calendar_removed is None
    calendar_removed = service_calendar.remove(None)
    assert calendar_removed is None


def test_update_calendar(service_calendar, calendar_create,
                         calendar_update, service_user):
    """
    Test updating calendar.
    """
    user = service_user.get_by_token("fkbwa;uwfgagflwy")
    calendar = service_calendar.create_calendar(calendar_create, user)
    calendar_updated = service_calendar.update_calendar(
        calendar.calendar_id,
        calendar_update,
        user
    )

    assert calendar_updated is not None
    assert calendar_updated.max_people == calendar_update.max_people


def test_get_all(service_calendar, calendar_create):
    """
    Test getting all calendars.
    """
    calendars = service_calendar.get_all()
    assert calendars is not None
    service_calendar.remove(calendar_create.calendar_id)
    calendars = service_calendar.get_all()
    assert calendars is None
