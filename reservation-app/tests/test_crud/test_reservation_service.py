"""Module for testing reservation service crud."""

import pytest
from core.models import CalendarModel, EventState, MiniServiceModel
from core.schemas import ReservationServiceUpdate


@pytest.mark.asyncio
async def test_create_reservation_service(test_reservation_service):
    """Test creating reservation service."""
    assert test_reservation_service.name == "Study Room"
    assert test_reservation_service.alias == "study"
    assert test_reservation_service.public is True


@pytest.mark.asyncio
async def test_get_reservation_service_by_id(
    test_reservation_service,
    reservation_service_crud,
):
    """Test getting reservation service by id."""
    db_reservation_service = await reservation_service_crud.get(
        test_reservation_service.id,
    )
    assert db_reservation_service is not None
    assert db_reservation_service.name == test_reservation_service.name
    assert db_reservation_service.id == test_reservation_service.id
    assert db_reservation_service.alias == test_reservation_service.alias


@pytest.mark.asyncio
async def test_get_by_name_reservation_service(
    test_reservation_service,
    reservation_service_crud,
):
    """Test getting reservation service by name."""
    service = await reservation_service_crud.get_by_name("Study Room")
    assert service is not None
    assert service.alias == test_reservation_service.alias


@pytest.mark.asyncio
async def test_get_by_alias_reservation_service(
    test_reservation_service,
    reservation_service_crud,
):
    """Test getting reservation service by alias."""
    service = await reservation_service_crud.get_by_alias("study")
    assert service is not None
    assert service.name == test_reservation_service.name


@pytest.mark.asyncio
async def test_get_all_reservation_services(
    reservation_service_crud,
    test_reservation_service,
    test_reservation_service2,
):
    """Test retrieving all reservation services."""
    services = await reservation_service_crud.get_all()
    names = [service.name for service in services]

    assert len(services) >= 2
    assert test_reservation_service.name in names
    assert test_reservation_service2.name in names


@pytest.mark.asyncio
async def test_get_multi_reservation_services(
    reservation_service_crud,
    test_reservation_service,
    test_reservation_service2,
):
    """Test retrieving limited reservation services."""
    services = await reservation_service_crud.get_multi(limit=1)
    names = [service.name for service in services]
    assert len(services) == 1
    if test_reservation_service.name in names:
        assert test_reservation_service.name in names
        assert test_reservation_service2.name not in names
    else:
        assert test_reservation_service.name not in names
        assert test_reservation_service2.name in names


@pytest.mark.asyncio
async def test_get_all_aliases(
    reservation_service_crud,
    test_reservation_service,
    test_reservation_service2,
):
    """Test retrieving all aliases."""
    aliases = await reservation_service_crud.get_all_aliases()
    assert test_reservation_service.alias in aliases
    assert test_reservation_service2.alias in aliases


@pytest.mark.asyncio
async def test_get_public_services(
    reservation_service_crud,
    test_reservation_service,
    test_reservation_service2,
):
    """Test retrieving all public services."""
    public_services = await reservation_service_crud.get_public_services()
    public_names = [service.name for service in public_services]

    assert test_reservation_service.name in public_names
    assert test_reservation_service2.name not in public_names  # second one is not public


@pytest.mark.asyncio
async def test_update_reservation_service(
    test_reservation_service,
    reservation_service_crud,
):
    """Test updating reservation service."""
    updated = await reservation_service_crud.update(
        db_obj=test_reservation_service,
        obj_in=ReservationServiceUpdate(name="Updated name", public=False),
    )
    assert updated.name == "Updated name"
    assert updated.public is False


@pytest.mark.asyncio
async def test_soft_remove_reservation_service(
    test_reservation_service,
    reservation_service_crud,
):
    """Test soft deleting reservation service."""
    soft_removed = await reservation_service_crud.soft_remove(
        test_reservation_service,
    )
    assert soft_removed.deleted_at is not None


@pytest.mark.asyncio
async def test_retrieve_soft_removed_reservation_service(
    test_reservation_service,
    reservation_service_crud,
):
    """Test restoring soft deleted reservation service."""
    await reservation_service_crud.soft_remove(test_reservation_service)
    restored = await reservation_service_crud.restore(
        test_reservation_service,
    )
    assert restored is not None
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_hard_remove_reservation_service(
    test_reservation_service,
    reservation_service_crud,
):
    """Test hard deleting reservation service."""
    removed = await reservation_service_crud.remove(test_reservation_service.id)
    assert removed is not None
    assert removed.id == test_reservation_service.id

    should_be_none = await reservation_service_crud.get(removed.id)
    assert should_be_none is None


@pytest.mark.asyncio
async def test_get_by_name_include_removed(
    reservation_service_crud,
    test_reservation_service,
):
    """Test retrieving a soft-deleted reservation service by name with include_removed=True."""
    await reservation_service_crud.soft_remove(test_reservation_service)
    service = await reservation_service_crud.get_by_name(
        name=test_reservation_service.name,
        include_removed=True,
    )
    assert service is not None
    assert service.name == test_reservation_service.name
    assert service.deleted_at is not None


@pytest.mark.asyncio
async def test_get_by_alias_include_removed(
    reservation_service_crud,
    test_reservation_service,
):
    """Test retrieving a soft-deleted reservation service by alias with include_removed=True."""
    await reservation_service_crud.soft_remove(test_reservation_service)
    service = await reservation_service_crud.get_by_alias(
        alias=test_reservation_service.alias,
        include_removed=True,
    )
    assert service is not None
    assert service.alias == test_reservation_service.alias
    assert service.deleted_at is not None


@pytest.mark.asyncio
async def test_get_public_services_include_removed(
    reservation_service_crud,
    test_reservation_service,
    test_reservation_service2,
):
    """Test retrieving public services including soft-deleted ones."""
    await reservation_service_crud.soft_remove(test_reservation_service)
    services = await reservation_service_crud.get_public_services(include_removed=True)
    assert any(service.id == test_reservation_service.id for service in services)
    assert test_reservation_service != test_reservation_service2


@pytest.mark.asyncio
async def test_get_all_aliases_empty(reservation_service_crud):
    """Test retrieving all aliases when no services exist."""
    aliases = await reservation_service_crud.get_all_aliases()
    assert isinstance(aliases, list)
    assert len(aliases) == 0


@pytest.mark.asyncio
async def test_get_calendars_by_reservation_service_id(
    reservation_service_crud, test_reservation_service, test_calendar
):
    """Test retrieving calendars by reservation service ID."""
    calendars = await reservation_service_crud.get_related_entities_by_reservation_service_id(
        CalendarModel, test_reservation_service.id, True
    )
    assert any(cal.id == test_calendar.id for cal in calendars)


@pytest.mark.asyncio
async def test_get_mini_services_by_reservation_service_id(
    reservation_service_crud, test_reservation_service, test_mini_service
):
    """Test retrieving calendars by reservation service ID."""
    mini_services = await reservation_service_crud.get_related_entities_by_reservation_service_id(
        MiniServiceModel, test_reservation_service.id
    )
    assert any(mini_service.id == test_mini_service.id for mini_service in mini_services)


@pytest.mark.asyncio
async def test_get_by_room_id(reservation_service_crud, test_reservation_service):
    """Test retrieving reservation service by room id."""
    updated = await reservation_service_crud.update(
        db_obj=test_reservation_service,
        obj_in=ReservationServiceUpdate(room_id=1),
    )
    service = await reservation_service_crud.get_by_room_id(updated.room_id)
    assert service.room_id == 1
    soft_removed = await reservation_service_crud.soft_remove(
        service,
    )
    assert soft_removed.deleted_at is not None
    service_removed = await reservation_service_crud.get_by_room_id(updated.room_id, True)
    assert service_removed.room_id == 1


@pytest.mark.asyncio
async def test_get_events_by_reservation_service_id_empty(
    reservation_service_crud, test_reservation_service
):
    """Test getting events by reservation service id empty."""
    events = await reservation_service_crud.get_events_by_reservation_service_id(
        test_reservation_service.id
    )
    assert events == []


@pytest.mark.asyncio
async def test_get_events_by_reservation_service_id(
    reservation_service_crud,
    test_reservation_service,
    test_event,
):
    """Test getting events by reservation service id."""
    events = await reservation_service_crud.get_events_by_reservation_service_id(
        test_reservation_service.id, EventState.CONFIRMED
    )
    assert events[0].id == test_event.id
    assert events[0].event_state == test_event.event_state
    assert events[0].purpose == test_event.purpose
