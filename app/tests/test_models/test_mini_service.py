"""
Module for testing mini service model
"""
from models import MiniServiceModel


def test_create_mini_service(db_session, create_uuid):
    """
    Test creating mini service model.
    """
    db_obj = MiniServiceModel(
        uuid=create_uuid,
        name="Bar",
        service_alias="klub"
    )

    db_session.add(db_obj)
    db_session.commit()
    db_session.refresh(db_obj)
    assert db_obj is not None


def test_get_created_mini_service(db_session, create_uuid):
    """
    Test get creating mini service model.
    """
    db_obj = db_session.get(MiniServiceModel, create_uuid)
    assert db_obj.uuid == create_uuid
    assert db_obj.name == "Bar" and db_obj.service_alias == "klub"
