"""Conftest for testing crud."""

import datetime as dt
import pytest
import pytest_asyncio
from core.models.event import EventState
from core.schemas import (
    CalendarCreate,
    MiniServiceCreate,
    ReservationServiceCreate,
    Rules,
    UserCreate,
    EventLite,
)
from crud import CRUDCalendar, CRUDMiniService, CRUDReservationService, CRUDUser, CRUDEvent


@pytest.fixture
def user_crud(async_session):
    """Return user crud."""
    return CRUDUser(db=async_session)


@pytest.fixture
def reservation_service_crud(async_session):
    """Return reservation service crud."""
    return CRUDReservationService(db=async_session)


@pytest.fixture
def mini_service_crud(async_session):
    """Return mini service crud."""
    return CRUDMiniService(db=async_session)


@pytest.fixture
def calendar_crud(async_session):
    """Return calendar crud."""
    return CRUDCalendar(db=async_session)


@pytest.fixture
def event_crud(async_session):
    """Return event crud."""
    return CRUDEvent(db=async_session)


@pytest_asyncio.fixture
async def test_user(user_crud):
    """Create and return a test user."""
    user = await user_crud.create(
        UserCreate(
            id=2142,
            username="fixture_user",
            full_name="Fixture Gabel",
            active_member=True,
            section_head=False,
            roles=["club", "grill"],
        ),
    )
    return user


@pytest_asyncio.fixture
async def test_user2(user_crud):
    """Create and return a test user2."""
    user = await user_crud.create(
        UserCreate(
            id=6545,
            username="test_user2",
            full_name="Barin Gabel",
            active_member=False,
            section_head=True,
            roles=["study", "games"],
        ),
    )
    return user


@pytest_asyncio.fixture
async def test_reservation_service(reservation_service_crud):
    """Create and return a test reservation service."""
    reservation_service = await reservation_service_crud.create(
        ReservationServiceCreate(
            name="Study Room",
            alias="study",
            web="https://study.room.cz",
            contact_mail="study.test.room@buk.cvut.cz",
            public=True,
        ),
    )
    return reservation_service


@pytest_asyncio.fixture
async def test_reservation_service2(reservation_service_crud):
    """Create and return a test reservation service2."""
    reservation_service = await reservation_service_crud.create(
        ReservationServiceCreate(
            name="Grill",
            alias="grill",
            web="https://grill.cz",
            contact_mail="grill.test@buk.cvut.cz",
            public=False,
        ),
    )
    return reservation_service


@pytest_asyncio.fixture
async def test_mini_service(mini_service_crud, test_reservation_service):
    """Create and return a test mini service."""
    mini_service = await mini_service_crud.create(
        MiniServiceCreate(
            name="Projector",
            reservation_service_id=test_reservation_service.id,
        ),
    )
    return mini_service


@pytest_asyncio.fixture
async def test_mini_service2(mini_service_crud, test_reservation_service):
    """Create and return a test mini service2."""
    mini_service = await mini_service_crud.create(
        MiniServiceCreate(
            name="Bar",
            reservation_service_id=test_reservation_service.id,
        ),
    )
    return mini_service


@pytest.fixture(scope="module")
def calendar_rules() -> Rules:
    """Return rules schemas."""
    return Rules(
        night_time=True,
        reservation_without_permission=True,
        max_reservation_hours=18,
        in_advance_hours=12,
        in_advance_minutes=60,
        in_prior_days=30,
    )


@pytest_asyncio.fixture
async def test_calendar(
    calendar_crud,
    calendar_rules,
    test_reservation_service,
):
    """Create and return a test calendar."""
    calendar = await calendar_crud.create_with_mini_services_and_collisions(
        CalendarCreate(
            id="fixteure.calen.id@exgogl.eu",
            reservation_type="Grillcentrum",
            color="#fe679",
            max_people=15,
            more_than_max_people_with_permission=False,
            collision_with_itself=False,
            club_member_rules=calendar_rules,
            active_member_rules=calendar_rules,
            manager_rules=calendar_rules,
            reservation_service_id=test_reservation_service.id,
        ),
        [],
    )
    return calendar


@pytest_asyncio.fixture
async def test_calendar2(
    calendar_crud,
    calendar_rules,
    test_reservation_service2,
    test_calendar,
):
    """Create and return a test calendar."""
    calendar = await calendar_crud.create_with_mini_services_and_collisions(
        CalendarCreate(
            id="klubar.calen.id@exgogl.eu",
            reservation_type="Klubovna",
            color="#fe375",
            max_people=10,
            more_than_max_people_with_permission=False,
            collision_with_itself=False,
            club_member_rules=calendar_rules,
            active_member_rules=calendar_rules,
            manager_rules=calendar_rules,
            reservation_service_id=test_reservation_service2.id,
            collision_ids=[test_calendar.id],
        ),
        [],
    )
    return calendar


# @pytest_asyncio.fixture
# async def test_event(event_crud, test_user, test_calendar_service):
#     """Create and return a test event."""
#     start = dt.datetime.now().replace(microsecond=0)
#     end = start + dt.timedelta(hours=2)
#
#     event = await event_crud.create(
#         EventLite(
#             id="some-test-id",
#             reservation_start=start,
#             reservation_end=end,
#             purpose="Workshop",
#             guests=5,
#             calendar_id=test_calendar_service.id,
#             user_id=test_user.id,
#             email="user@example.com",
#             event_state=EventState.CONFIRMED,
#         )
#     )
#     return event
#
#
# @pytest_asyncio.fixture
# async def test_event2(event_crud, test_user2, test_calendar_service):
#     """Create and return another test event."""
#     start = dt.datetime.now().replace(microsecond=0) + dt.timedelta(days=1)
#     end = start + dt.timedelta(hours=3)
#
#     event = await event_crud.create(
#         EventLite(
#             id="some-test-id2",
#             reservation_start=start,
#             reservation_end=end,
#             purpose="Lecture",
#             guests=10,
#             calendar_id=test_calendar_service.id,
#             user_id=test_user2.id,
#             email="user2@example.com",
#             event_state=EventState.CONFIRMED,
#         )
#     )
#     return event
