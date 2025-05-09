"""
Module for testing user model
"""
from models import UserModel
import sqlalchemy
import pytest


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_create_user(test_user):
    """
    Test creating user model.
    """
    assert test_user.id == 2142
    assert test_user.username == "TestUser"
    assert test_user.roles == ["Bar", "Consoles"]


@pytest.mark.asyncio
async def test_get_user(async_session, test_user):
    """
    Test getting the user from the database.
    """
    db_obj = await async_session.get(UserModel, test_user.id)
    assert db_obj is not None
    assert db_obj.username == test_user.username


@pytest.mark.asyncio
async def test_update_user(async_session, test_user):
    """
    Test updating the test user.
    """
    test_user.username = "CoolRader"
    await async_session.commit()
    await async_session.refresh(test_user)
    assert test_user.username == "CoolRader"


@pytest.mark.asyncio
async def test_delete_user(async_session, test_user):
    """
    Test deleting the test user.
    """
    await async_session.delete(test_user)
    await async_session.commit()
    deleted = await async_session.get(UserModel, test_user.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_list_users(async_session):
    """
    Test listing multiple users.
    """
    users = [
        UserModel(
            id=1,
            username="User1",
            full_name="dfwa dfwanfw",
            room_number="896",
            active_member=True,
            section_head=False,
            roles=["TeamA"],
        ),
        UserModel(
            id=2,
            username="User2",
            full_name="Kagar Lavi",
            room_number="8978",
            active_member=False,
            section_head=True,
            roles=["TeamB"],
        ),
    ]
    async_session.add_all(users)
    await async_session.commit()

    result = (await async_session.execute(
        sqlalchemy.select(UserModel)
    )).scalars().all()

    assert len(result) == 2
    usernames = [u.username for u in result]
    assert "User1" in usernames
    assert "User2" in usernames
