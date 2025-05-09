"""
Conftest for testing model
"""
import uuid
import pytest
import pytest_asyncio
from models import UserModel, ReservationServiceModel, \
    MiniServiceModel, CalendarModel
from schemas import Rules


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest

# pylint: disable=duplicate-code
# reason: needed for testing; similar conftests are intentionally
# separated by the model they belong to


@pytest.fixture(scope="module")
def create_reservation_service_uuid():
    """
    Fixture that create uuid.
    """
    return uuid.uuid4()


@pytest.fixture(scope="module")
def create_mini_service_uuid():
    """
    Fixture that create uuid.
    """
    return uuid.uuid4()


@pytest.mark.asyncio
@pytest_asyncio.fixture
async def test_user(async_session):
    """
    Creates and returns a sample user for testing.
    """
    user = UserModel(
        id=2142,
        username="TestUser",
        full_name="test testovi",
        room_number="6343",
        active_member=False,
        section_head=False,
        roles=["Bar", "Consoles"],
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.mark.asyncio
@pytest_asyncio.fixture
async def test_reservation_service(async_session, create_reservation_service_uuid):
    """
    Creates and returns a sample reservation service for testing.
    """
    reservation_service = ReservationServiceModel(
        id=create_reservation_service_uuid,
        name="Club Room",
        alias="club",
        public=True,
        web="test@example.com",
        contact_mail="club.room.test@buk.cvut.cz"
    )
    async_session.add(reservation_service)
    await async_session.commit()
    await async_session.refresh(reservation_service)
    return reservation_service


@pytest.mark.asyncio
@pytest_asyncio.fixture
async def test_mini_service(async_session,
                            create_mini_service_uuid,
                            test_reservation_service):
    """
    Creates and returns a sample reservation service for testing.
    """
    mini_service = MiniServiceModel(
        id=create_mini_service_uuid,
        name="Bar",
        reservation_service_id=test_reservation_service.id
    )
    async_session.add(mini_service)
    await async_session.commit()
    await async_session.refresh(mini_service)
    return mini_service


@pytest.fixture(scope="module")
def rules_club_member() -> Rules:
    """
    Return rules schemas.
    """
    return Rules(
        night_time=False,
        reservation_without_permission=True,
        max_reservation_hours=24,
        in_advance_hours=24,
        in_advance_minutes=30,
        in_prior_days=14
    )


@pytest.mark.asyncio
@pytest_asyncio.fixture
async def test_calendar(async_session,
                        rules_club_member,
                        test_reservation_service):
    """
    Creates and returns a sample calendar for testing.
    """
    calendar = CalendarModel(
        id="test_calendar@google.com",
        reservation_type="Entire Space",
        color="#00ffcc",
        max_people=10,
        more_than_max_people_with_permission=True,
        collision_with_itself=True,
        collision_with_calendar=["other_calendar_id"],
        club_member_rules=rules_club_member,
        active_member_rules=rules_club_member,
        manager_rules=rules_club_member,
        reservation_service_id=test_reservation_service.id,
        mini_services=["Bar"]
    )
    async_session.add(calendar)
    await async_session.commit()
    await async_session.refresh(calendar)
    return calendar
