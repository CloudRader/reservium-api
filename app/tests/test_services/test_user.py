"""
Module for testing user service
"""
import pytest
from schemas import UserCreate


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_user_service_create_new_user(server_create_user):
    """
    Test creating a new user via UserService.
    """
    new_user = await server_create_user

    assert new_user.id == 1111
    assert new_user.username == "kanya_garin"
    assert new_user.active_member is False
    assert new_user.section_head is False


@pytest.mark.asyncio
async def test_user_service_update_existing_user(server_create_user):
    """
    Test updating an existing user via UserService.
    """
    updated_user = await server_create_user

    assert updated_user.active_member is False
    assert updated_user.section_head is False


@pytest.mark.asyncio
async def test_user_service_create_user_section_head(service_user,
                                                     user_data_from_is,
                                                     services_data_from_is,
                                                     room_data_from_is):
    """
    Test auto-setting section_head when note='head' in UserIS.
    """
    user_data_from_is.note = "head"
    new_user = await service_user.create_user(
        user_data=user_data_from_is,
        roles=[],
        services=services_data_from_is,
        room=room_data_from_is,
    )

    assert new_user.section_head is True
    assert new_user.active_member is True


@pytest.mark.asyncio
async def test_user_service_get_by_username(service_user):
    """
    Test retrieving user by username.
    """
    user_data = UserCreate(
        id=2141,
        username="test_user",
        full_name="=Gagir Bakalar",
        room_number="54875",
        active_member=True,
        section_head=False,
        roles=[],
    )
    await service_user.create(user_data)
    fetched = await service_user.get_by_username("test_user")

    assert fetched.username == "test_user"


@pytest.mark.asyncio
async def test_user_service_get_by_username_not_found(service_user):
    """
    Test retrieving a nonexistent username returns None.
    """
    result = await service_user.get_by_username("does_not_exist")
    assert result is None
