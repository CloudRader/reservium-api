"""Module for testing event service crud."""

import pytest
from core.schemas import EventUpdate


@pytest.mark.asyncio
async def test_create_event(test_event):
    """Test creating an event."""
    assert test_event.purpose == "Workshop"
    assert test_event.guests == 5
    assert test_event.email == "user@example.com"


@pytest.mark.asyncio
async def test_get_event_by_id(test_event, event_crud):
    """Test getting event by ID."""
    db_event = await event_crud.get(test_event.id)
    assert db_event is not None
    assert db_event.purpose == "Workshop"


@pytest.mark.asyncio
async def test_get_all_events(event_crud, test_event, test_event2):
    """Test retrieving all events."""
    events = await event_crud.get_all()
    ids = [e.id for e in events]
    assert test_event.id in ids
    assert test_event2.id in ids


@pytest.mark.asyncio
async def test_update_event(test_event, event_crud):
    """Test updating an event."""
    updated_event = await event_crud.update(
        db_obj=test_event, obj_in=EventUpdate(purpose="Updated Workshop")
    )
    assert updated_event.purpose == "Updated Workshop"


@pytest.mark.asyncio
async def test_soft_remove_event(test_event, event_crud):
    """Test soft deleting an event."""
    soft_removed = await event_crud.soft_remove(test_event)
    assert soft_removed.deleted_at is not None


@pytest.mark.asyncio
async def test_restore_event(test_event, event_crud):
    """Test restoring a soft-deleted event."""
    await event_crud.soft_remove(test_event)
    restored = await event_crud.restore(test_event)
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_hard_remove_event(test_event, event_crud):
    """Test hard deleting an event."""
    hard_removed = await event_crud.remove(test_event.id)
    assert hard_removed.id == test_event.id
    db_event = await event_crud.get(hard_removed.id)
    assert db_event is None
