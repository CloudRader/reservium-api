"""
Conftest for testing crud
"""
import pytest
import pytest_asyncio
from crud import CRUDUser, CRUDReservationService, CRUDMiniService, CRUDCalendar
from schemas import UserCreate, ReservationServiceCreate, \
    MiniServiceCreate, CalendarCreate, Rules


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest

# pylint: disable=duplicate-code
# reason: needed for testing; similar conftests are intentionally
# separated by the model they belong to


@pytest.fixture
def user_crud(async_session):
    """
    Return user crud.
    """
    return CRUDUser(db=async_session)


@pytest.fixture
def reservation_service_crud(async_session):
    """
    Return reservation service crud.
    """
    return CRUDReservationService(db=async_session)


@pytest.fixture
def mini_service_crud(async_session):
    """
    Return mini service crud.
    """
    return CRUDMiniService(db=async_session)


@pytest.fixture
def calendar_crud(async_session):
    """
    Return calendar crud.
    """
    return CRUDCalendar(db=async_session)


@pytest_asyncio.fixture
async def test_user(user_crud):
    """
    Creates and returns a test user.
    """
    user = await user_crud.create(UserCreate(
        id=2142,
        username="fixture_user",
        full_name="Fixture Gabel",
        room_number="20123",
        active_member=True,
        section_head=False,
        roles=["club", "grill"]
    ))
    return user


@pytest_asyncio.fixture
async def test_user2(user_crud):
    """
    Creates and returns a test user2.
    """
    user = await user_crud.create(UserCreate(
        id=6545,
        username="test_user2",
        full_name="Barin Gabel",
        room_number="865",
        active_member=False,
        section_head=True,
        roles=["study", "games"]
    ))
    return user


@pytest_asyncio.fixture
async def test_reservation_service(reservation_service_crud):
    """
    Creates and returns a test reservation service.
    """
    reservation_service = await reservation_service_crud.create(
        ReservationServiceCreate(
            name="Study Room",
            alias="study",
            web="https://study.room.cz",
            contact_mail="study.test.room@buk.cvut.cz",
            public=True
        ))
    return reservation_service


@pytest_asyncio.fixture
async def test_reservation_service2(reservation_service_crud):
    """
    Creates and returns a test reservation service2.
    """
    reservation_service = await reservation_service_crud.create(
        ReservationServiceCreate(
            name="Grill",
            alias="grill",
            web="https://grill.cz",
            contact_mail="grill.test@buk.cvut.cz",
            public=False
        ))
    return reservation_service


@pytest_asyncio.fixture
async def test_mini_service(mini_service_crud,
                            test_reservation_service):
    """
    Creates and returns a test mini service.
    """
    mini_service = await mini_service_crud.create(
        MiniServiceCreate(
            name="Projector",
            reservation_service_id=test_reservation_service.id
        ))
    return mini_service


@pytest_asyncio.fixture
async def test_mini_service2(mini_service_crud,
                             test_reservation_service):
    """
    Creates and returns a test mini service2.
    """
    mini_service = await mini_service_crud.create(
        MiniServiceCreate(
            name="Bar",
            reservation_service_id=test_reservation_service.id
        ))
    return mini_service


@pytest.fixture(scope="module")
def calendar_rules() -> Rules:
    """
    Return rules schemas.
    """
    return Rules(
        night_time=True,
        reservation_without_permission=True,
        max_reservation_hours=18,
        in_advance_hours=12,
        in_advance_minutes=60,
        in_prior_days=30
    )


@pytest_asyncio.fixture
async def test_calendar_service(calendar_crud,
                                calendar_rules,
                                test_reservation_service):
    """
    Creates and returns a test calendar.
    """
    calendar = await calendar_crud.create(
        CalendarCreate(
            id="fixteure.calen.id@exgogl.eu",
            reservation_type="Grillcentrum",
            color="#fe679",
            max_people=15,
            more_than_max_people_with_permission=False,
            collision_with_itself=False,
            collision_with_calendar=["club_room_example_id"],
            club_member_rules=calendar_rules,
            active_member_rules=calendar_rules,
            manager_rules=calendar_rules,
            reservation_service_id=test_reservation_service.id,
            mini_services=["Console", "Bar", "Projector"]
        ))
    return calendar
