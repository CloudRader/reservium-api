"""
Module for testing document service.
"""


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


def test_create_user(service_user, user_create):
    """
    Test creating user.
    """
    user = service_user.create(user_create)
    assert user is not None


def test_delete_user(service_user, user_create):
    """
    Test deleting user.
    """
    db_user = service_user.get_by_username(user_create.username)
    removed_user = service_user.remove(db_user.uuid)
    assert removed_user is not None
    assert removed_user.uuid == db_user.uuid
    db_user = service_user.get_by_username(removed_user.username)
    assert db_user is None


def test_create_user_with_data_from_is(
        service_user, user_data_from_is,
        roles_data_from_is
):
    """
    Test creating user with data from IS.
    """
    user = service_user.create_user(user_data_from_is,
                                    roles_data_from_is,
                                    "kfh5y7t7gf4gsfg4lo")
    assert user is not None


def test_get_by_username(service_user):
    """
    Test getting created user by username.
    """
    db_user = service_user.get_by_username("kanya_garin")
    assert db_user is not None


def test_get_by_token(service_user):
    """
    Test getting created user by token.
    """
    db_user = service_user.get_by_token("kfh5y7t7gf4gsfg4lo")
    assert db_user is not None


def test_update_user(service_user, user_create,
                     user_update):
    """
    Test updating user.
    """
    user = service_user.create(obj_in=user_create)
    user_to_update = service_user.get(user.uuid)
    user_updated = service_user.update(user_to_update.uuid,
                                       user_update)

    assert user_updated is not None
    assert user_updated.active_member == user_update.active_member


def test_remove_nonexistent_user(service_user):
    """
    Test deleting nonexistent user.
    """
    user = service_user.get_by_username("kanya_garin")
    user_removed = service_user.remove(user.uuid)
    assert user_removed is not None
    user_removed = service_user.remove(user_removed.uuid)
    assert user_removed is None
    user_removed = service_user.remove(None)
    assert user_removed is None
