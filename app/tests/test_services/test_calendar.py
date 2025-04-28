"""
Module for testing mini service ser.
"""
import pytest
from schemas import CalendarUpdate
from api import PermissionDeniedException, BaseAppException


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
async def test_create_calendar(calendar,
                               calendar_create):
    """
    Test creating a calendar.
    """
    assert calendar is not None
    assert calendar.reservation_type == calendar_create.reservation_type
    assert calendar.club_member_rules == calendar_create.club_member_rules
    assert (calendar.reservation_service_id ==
            calendar_create.reservation_service_id)


@pytest.mark.asyncio
async def test_create_calendar_no_permission(service_calendar,
                                             calendar_create,
                                             user_not_head):
    """
    Test creating a mini service when the user doesn't have permission.
    """
    with pytest.raises(PermissionDeniedException):
        await service_calendar.create_calendar(
            calendar_create, user_not_head
        )


@pytest.mark.asyncio
async def test_create_calendar_collision_not_found(service_calendar,
                                                   calendar_create,
                                                   user):
    """
    Test that creating a calendar with a non-existent collision calendar raises an error.
    """
    calendar_create.collision_with_calendar = ["non-existent-calendar-id"]
    with pytest.raises(BaseAppException):
        await service_calendar.create_calendar(calendar_create, user)


@pytest.mark.asyncio
async def test_create_calendar_with_existing_reservation_type(service_calendar,
                                                              calendar_create,
                                                              user):
    """
    Test that creating a calendar with an already existing reservation type raises an error.
    """
    await service_calendar.create_calendar(calendar_create, user)
    with pytest.raises(BaseAppException):
        await service_calendar.create_calendar(calendar_create, user)


@pytest.mark.asyncio
async def test_get_calendar(service_calendar,
                            calendar):
    """
    Test getting a calendar.
    """
    get_calendar = await service_calendar.get(
        calendar.id
    )
    assert get_calendar is not None
    assert get_calendar.reservation_type == calendar.reservation_type
    assert get_calendar.club_member_rules == calendar.club_member_rules
    assert (get_calendar.reservation_service_id ==
            calendar.reservation_service_id)


@pytest.mark.asyncio
async def test_get_calendar_by_reservation_type(service_calendar,
                                                calendar):
    """
    Test getting a calendar by reservation type.
    """
    get_calendar = await service_calendar.get_by_reservation_type(
        calendar.reservation_type
    )
    assert get_calendar is not None
    assert get_calendar.reservation_type == calendar.reservation_type
    assert get_calendar.club_member_rules == calendar.club_member_rules
    assert (get_calendar.reservation_service_id ==
            calendar.reservation_service_id)


@pytest.mark.asyncio
async def test_get_reservation_service_of_this_calendar(service_calendar,
                                                        calendar,
                                                        reservation_service):
    """
    Test getting a reservation service of this calendar.
    """
    get_reservation_service = await service_calendar.get_reservation_service_of_this_calendar(
        calendar.reservation_service_id
    )
    assert get_reservation_service is not None
    assert get_reservation_service.name == reservation_service.name
    assert get_reservation_service.id == reservation_service.id
    assert get_reservation_service.web == reservation_service.web


@pytest.mark.asyncio
async def test_get_calendars_by_reservation_service_id(service_calendar,
                                                       calendar):
    """
    Test getting a calendar by reservation service id.
    """
    get_calendars = await service_calendar.get_by_reservation_service_id(
        calendar.reservation_service_id
    )
    assert get_calendars != []
    assert get_calendars[0].reservation_type == calendar.reservation_type
    assert (get_calendars[0].reservation_service_id ==
            calendar.reservation_service_id)


@pytest.mark.asyncio
async def test_update_mini_service(service_calendar,
                                   calendar,
                                   user):
    """
    Test updating an existing calendar.
    """
    calendar_update = CalendarUpdate(
        reservation_type="Updated Galambula",
    )

    updated_service = await service_calendar.update_calendar(
        calendar.id, calendar_update, user
    )

    assert updated_service is not None
    assert updated_service.reservation_type == calendar_update.reservation_type
    assert updated_service.reservation_service_id == calendar.reservation_service_id


@pytest.mark.asyncio
async def test_update_mini_service_no_permission(service_calendar,
                                                 calendar,
                                                 user_not_head):
    """
    Test updating a calendar when the user doesn't have permission.
    """
    calendar_update = CalendarUpdate(
        reservation_type="Updated Galambula",
    )

    with pytest.raises(PermissionDeniedException):
        await service_calendar.update_calendar(
            calendar.id, calendar_update, user_not_head
        )


@pytest.mark.asyncio
async def test_soft_delete_calendar(service_calendar,
                                    calendar,
                                    user):
    """
    Test soft deleting a calendar.
    """
    soft_removed_service = await service_calendar.delete_calendar(
        calendar.id, user, hard_remove=False
    )

    assert soft_removed_service is not None
    assert soft_removed_service.id == calendar.id


@pytest.mark.asyncio
async def test_hard_delete_calendar(service_calendar,
                                    calendar,
                                    user):
    """
    Test hard deleting a calendar.
    """
    hard_removed_service = await service_calendar.delete_calendar(
        calendar.id, user, hard_remove=True
    )

    assert hard_removed_service is not None
    assert hard_removed_service.id == calendar.id


@pytest.mark.asyncio
async def test_delete_calendar_no_permission(service_calendar,
                                             calendar,
                                             user_not_head):
    """
    Test deleting a calendar when the user doesn't have permission.
    """
    with pytest.raises(PermissionDeniedException):
        await service_calendar.delete_calendar(
            calendar.id, user_not_head, hard_remove=False
        )


@pytest.mark.asyncio
async def test_delete_non_existent_calendar(service_calendar, user):
    """
    Test deleting a calendar that doesn't exist.
    """
    delete_not_exist_calendar = await service_calendar.delete_calendar("non-existent-id",
                                                                       user,
                                                                       hard_remove=False)
    assert delete_not_exist_calendar is None


@pytest.mark.asyncio
async def test_retrieve_soft_removed_calendar(service_calendar,
                                              calendar,
                                              user):
    """
    Test restoring soft deleted calendar.
    """
    soft_removed_calendar = await service_calendar.delete_calendar(
        calendar.id, user, hard_remove=False
    )
    assert soft_removed_calendar.deleted_at is not None
    restored = await service_calendar.retrieve_removed_object(
        soft_removed_calendar.id, user
    )
    assert restored is not None
    assert restored.deleted_at is None


@pytest.mark.asyncio
async def test_retrieve_non_deleted_calendar(service_calendar, calendar, user):
    """
    Test retrieving a calendar that hasn't been softly deleted.
    """
    with pytest.raises(BaseAppException):
        await service_calendar.retrieve_removed_object(
            calendar.id, user
        )


@pytest.mark.asyncio
async def test_get_all_google_calendar_to_add(service_calendar,
                                              user):
    """
    Test getting all Google calendars that can be added by a user.
    """
    # Simulate the list of Google calendars
    google_calendars_data = {
        'items': [
            {'id': '1', 'accessRole': 'owner', 'primary': False},
            {'id': '2', 'accessRole': 'reader', 'primary': False},
            {'id': '3', 'accessRole': 'owner', 'primary': True},
            {'id': '4', 'accessRole': 'owner', 'primary': False},
        ]
    }
    new_calendars = await service_calendar.get_all_google_calendar_to_add(
        user, google_calendars_data
    )
    assert len(new_calendars) == 2
    assert new_calendars[0]['id'] == '1'
    assert new_calendars[1]['id'] == '4'
