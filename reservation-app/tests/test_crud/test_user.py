"""Module for testing user crud."""

import datetime as dt

import pytest
from core.schemas import EventUpdate, UserUpdate


@pytest.mark.asyncio
async def test_create_user(test_user):
    """Test creating user."""
    assert test_user.username == "fixture_user"
    assert test_user.active_member is True
    assert "club" in test_user.roles


@pytest.mark.asyncio
async def test_get_user_by_id(test_user, user_crud):
    """Test getting created user by id."""
    db_user = await user_crud.get(test_user.id)
    assert db_user is not None
    assert db_user.username == "fixture_user"


@pytest.mark.asyncio
async def test_get_user_by_username(test_user, user_crud):
    """Test getting created user by username."""
    db_user = await user_crud.get_by_username(test_user.username)
    assert db_user is not None
    assert db_user.username == "fixture_user"


@pytest.mark.asyncio
async def test_update_user(test_user, user_crud):
    """Test updating user."""
    user_updated = await user_crud.update(
        db_obj=test_user,
        obj_in=UserUpdate(section_head=True),
    )
    assert user_updated.section_head is True


@pytest.mark.asyncio
async def test_soft_remove_user(test_user, user_crud):
    """Test soft deleting user."""
    soft_removed = await user_crud.soft_remove(test_user)
    assert soft_removed.deleted_at is not None


@pytest.mark.asyncio
async def test_retrieve_soft_removed_user(test_user, user_crud):
    """Test retrieving from soft deleted user."""
    await user_crud.soft_remove(test_user)
    user_restored = await user_crud.restore(test_user)
    assert user_restored.deleted_at is None


@pytest.mark.asyncio
async def test_hard_remove_user(test_user, user_crud):
    """Test hard deleting user."""
    user_hard_removed = await user_crud.remove(test_user.id)
    assert user_hard_removed is not None
    assert user_hard_removed.id == test_user.id
    db_user = await user_crud.get(user_hard_removed.id)
    assert db_user is None


@pytest.mark.asyncio
async def test_get_all_users(user_crud, test_user, test_user2):
    """Test retrieving all users."""
    users = await user_crud.get_all()
    usernames = [user.username for user in users]

    assert len(users) >= 2  # At least the two created
    assert test_user.username in usernames
    assert test_user2.username in usernames


@pytest.mark.asyncio
async def test_get_multi_users(user_crud, test_user, test_user2):
    """Test retrieving multi users."""
    users_limited = await user_crud.get_multi(limit=1)
    usernames = [user.username for user in users_limited]
    assert len(users_limited) == 1
    assert test_user.username not in usernames
    assert test_user2.username in usernames


@pytest.mark.asyncio
async def test_get_with_none(user_crud):
    """Test retrieving an object with None as ID (should return None)."""
    result = await user_crud.get(id_=None)
    assert result is None


@pytest.mark.asyncio
async def test_update_with_empty_dict(user_crud, test_user):
    """Test update with empty dictionary (should keep original data)."""
    updated_user = await user_crud.update(db_obj=test_user, obj_in={})
    assert updated_user.id == test_user.id
    assert updated_user.roles == test_user.roles


@pytest.mark.asyncio
async def test_get_events_by_user_id(user_crud, event_crud, test_user, test_event):
    """Test getting future events by user id."""
    events = await user_crud.get_events_by_user_id(test_user.id)
    assert events[0].id == test_event.id
    assert events[0].event_state == test_event.event_state
    assert events[0].purpose == test_event.purpose
    assert events[0].reservation_start == test_event.reservation_start
    assert events[0].reservation_end == test_event.reservation_end


@pytest.mark.asyncio
async def test_get_events_by_user_id_past(user_crud, event_crud, test_user, test_event):
    """Test getting past events by user id."""
    start_time = dt.datetime.now() - dt.timedelta(days=3, hours=3)
    end_time = dt.datetime.now() - dt.timedelta(days=3)
    updated_event = await event_crud.update(
        db_obj=test_event,
        obj_in=EventUpdate(reservation_start=start_time, reservation_end=end_time),
    )
    events = await user_crud.get_events_by_user_id(test_user.id, past=True)
    assert events[0].id == updated_event.id
    assert events[0].event_state == updated_event.event_state
    assert events[0].purpose == updated_event.purpose
    assert events[0].reservation_start == updated_event.reservation_start
    assert events[0].reservation_end == updated_event.reservation_end


@pytest.mark.asyncio
async def test_get_events_by_user_id_future(user_crud, event_crud, test_user, test_event):
    """Test getting future events by user id."""
    start_time = dt.datetime.now() + dt.timedelta(days=10)
    end_time = dt.datetime.now() + dt.timedelta(days=10, hours=3)
    updated_event = await event_crud.update(
        db_obj=test_event,
        obj_in=EventUpdate(reservation_start=start_time, reservation_end=end_time),
    )
    events = await user_crud.get_events_by_user_id(test_user.id, past=False)
    assert events[0].id == test_event.id
    assert events[0].event_state == test_event.event_state
    assert events[0].purpose == test_event.purpose
    assert events[0].reservation_start == updated_event.reservation_start
    assert events[0].reservation_end == updated_event.reservation_end
