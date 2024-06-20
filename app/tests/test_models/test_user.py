"""
Module for testing user model
"""
from models import UserModel


def test_create_user(db_session, create_uuid):
    """
    Test creating user model.
    """
    db_obj = UserModel(
        uuid=create_uuid,
        username="FunRader",
        user_token="fwafwafbwjabfhwvahfwvawf",
        active_member=False,
        roles=["Bar", "Consoles"],
    )

    db_session.add(db_obj)
    db_session.commit()
    db_session.refresh(db_obj)
    assert db_obj is not None


def test_get_created_user(db_session, create_uuid):
    """
    Test get creating user model.
    """
    db_obj = db_session.get(UserModel, create_uuid)
    assert db_obj.uuid == create_uuid
    assert db_obj.username == "FunRader"
    assert db_obj.user_token == "fwafwafbwjabfhwvahfwvawf"
    assert not db_obj.active_member
    assert db_obj.roles == ["Bar", "Consoles"]
