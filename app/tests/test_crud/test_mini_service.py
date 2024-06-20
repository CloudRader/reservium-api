"""
Module for testing mini service crud
"""
import pytest

from crud import CRUDMiniService


# Using fixtures as variables is a standard for pytest
# pylint: disable=redefined-outer-name

@pytest.fixture()
def mini_service_crud(db_session):
    """
    Return mini service crud.
    """
    return CRUDMiniService(db=db_session)


def test_create_mini_service(mini_service_crud, mini_service_create):
    """
    Test creating mini service.
    """
    mini_service = mini_service_crud.create(obj_in=mini_service_create)
    assert mini_service is not None


def test_get_created_mini_service(mini_service_crud, mini_service_create):
    """
    Test getting created mini service.
    """
    db_mini_service = mini_service_crud.get_by_name(mini_service_create.name)
    assert db_mini_service is not None


def test_delete_mini_service(mini_service_crud, mini_service_create):
    """
    Test deleting mini service.
    """
    db_mini_service = mini_service_crud.get_by_name(mini_service_create.name)
    removed_mini_service = mini_service_crud.remove(db_mini_service.uuid)
    assert removed_mini_service is not None
    assert removed_mini_service.uuid == db_mini_service.uuid
    db_mini_service = mini_service_crud.get_by_name(removed_mini_service.uuid)
    assert db_mini_service is None


def test_remove_nonexistent_mini_service(mini_service_crud, mini_service_create):
    """
    Test deleting nonexistent mini service.
    """
    mini_service = mini_service_crud.create(obj_in=mini_service_create)
    mini_service_removed = mini_service_crud.remove(mini_service.uuid)
    assert mini_service_removed is not None
    mini_service_removed = mini_service_crud.remove(mini_service_removed.uuid)
    assert mini_service_removed is None
    mini_service_removed = mini_service_crud.remove(None)
    assert mini_service_removed is None


def test_update_mini_service(mini_service_crud, mini_service_create,
                             mini_service_update):
    """
    Test updating mini service.
    """
    mini_service = mini_service_crud.create(obj_in=mini_service_create)
    mini_service_to_update = mini_service_crud.get(mini_service.uuid)
    mini_service_updated = mini_service_crud.update(db_obj=mini_service_to_update,
                                                    obj_in=mini_service_update)

    assert mini_service_updated is not None
    assert mini_service_updated.service_alias == mini_service_update.service_alias
