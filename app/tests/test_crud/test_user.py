"""
Module for testing user crud
"""
import pytest

from crud import CRUDUser


# Using fixtures as variables is a standard for pytest
# pylint: disable=redefined-outer-name

@pytest.fixture()
def user_crud(db_session):
    """
    Return user crud.
    """
    return CRUDUser(db=db_session)


def test_create_user(user_crud, user_create):
    """
    Test creating user.
    """
    user = user_crud.create(obj_in=user_create)
    assert user is not None


def test_get_created_user(user_crud, user_create):
    """
    Test getting created user.
    """
    db_user = user_crud.get_by_username(user_create.username)
    assert db_user is not None


def test_delete_user(user_crud, user_create):
    """
    Test deleting user.
    """
    db_user = user_crud.get_by_username(user_create.username)
    removed_user = user_crud.remove(db_user.uuid)
    assert removed_user is not None
    assert removed_user.uuid == db_user.uuid
    db_user = user_crud.get_by_username(removed_user.username)
    assert db_user is None


def test_remove_nonexistent_user(user_crud, user_create):
    """
    Test deleting nonexistent user.
    """
    user = user_crud.create(obj_in=user_create)
    user_removed = user_crud.remove(user.uuid)
    assert user_removed is not None
    user_removed = user_crud.remove(user_removed.uuid)
    assert user_removed is None
    user_removed = user_crud.remove(None)
    assert user_removed is None


def test_update_user(user_crud, user_create,
                     user_update):
    """
    Test updating user.
    """
    user = user_crud.create(obj_in=user_create)
    user_to_update = user_crud.get(user.uuid)
    user_updated = user_crud.update(db_obj=user_to_update,
                                    obj_in=user_update)

    assert user_updated is not None
    assert user_updated.active_member == user_update.active_member
