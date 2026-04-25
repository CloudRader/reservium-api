# """Module for testing user service."""
#
# import pytest
# from core.schemas import UserCreate
#
#
# @pytest.mark.asyncio
# async def test_user_service_create_new_user(server_create_user):
#     """Test creating a new user via UserService."""
#     new_user = await server_create_user
#
#     assert new_user.id == 1111
#     assert new_user.username == "kanya_garin"
#
#
#
# @pytest.mark.asyncio
# async def test_user_service_get_by_username(service_user):
#     """Test retrieving user by username."""
#     user_data = UserCreate(
#         id=2141,
#         username="test_user",
#         full_name="=Gagir Bakalar",
#         room_number="54875",
#         roles=[],
#     )
#     await service_user.create(user_data)
#     fetched = await service_user.get_by_username("test_user")
#
#     assert fetched.username == "test_user"
#
#
# @pytest.mark.asyncio
# async def test_user_service_get_by_username_not_found(service_user):
#     """Test retrieving a nonexistent username returns None."""
#     result = await service_user.get_by_username("does_not_exist")
#     assert result is None
