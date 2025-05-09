"""
Conftest for testing api
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from schemas import UserIS, UserCreate, ReservationServiceCreate, \
    Zone, Room
from crud import CRUDUser, CRUDReservationService
from app.main import app


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest

# pylint: disable=duplicate-code
# reason: needed for testing; similar conftests are intentionally
# separated by the model they belong to

# pylint: disable=import-outside-toplevel
# reason: circular import issue

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


@pytest_asyncio.fixture
async def user_service(shared_session):
    """
    Returns a UserService instance using the shared test session.
    """
    from services import UserService
    return UserService(db=shared_session)


@pytest_asyncio.fixture
async def usual_user_service(async_session):
    """
    Returns a UserService instance using the isolated async test session.
    """
    from services import UserService
    return UserService(db=async_session)


@pytest_asyncio.fixture
async def reservation_service_service(shared_session):
    """
    Returns a ReservationServiceService instance using the shared test session.
    """
    from services import ReservationServiceService
    return ReservationServiceService(db=shared_session)


@pytest_asyncio.fixture
async def client(user_service, reservation_service_service):
    """
    Provides a test HTTP client with overridden dependencies.
    """
    from services import UserService, ReservationServiceService
    app.dependency_overrides[UserService] = lambda: user_service
    app.dependency_overrides[ReservationServiceService] = lambda: reservation_service_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture()
def user_data_from_is() -> UserIS:
    """
    Return new UserIS schema.
    """
    return UserIS(
        country="Czech Republic",
        created_at="2024-6-12",
        email="raina@buk.cvut.cz",
        first_name="Kanya",
        id=1111,
        im=None,
        note="active",
        organization=None,
        phone="+420",
        phone_vpn="+420-haa",
        photo_file="fhwa7owfyagof",
        photo_file_small="fwafwafafw",
        state="active",
        surname="Garin",
        ui_language="cz",
        ui_skin="Dark",
        username="kanya_garin",
        usertype="individual",
    )


@pytest.fixture()
def zone_data_from_is() -> Zone:
    """
    Return new Zone schema.
    """
    return Zone(
        alias="game",
        id=21,
        name="test.name",
        note="some.note"
    )


@pytest.fixture()
def room_data_from_is(zone_data_from_is) -> Room:
    """
    Return new Room schema.
    """
    return Room(
        door_number="215",
        floor=2,
        id=22,
        name="best.room",
        zone=zone_data_from_is,
    )


@pytest_asyncio.fixture
async def user(user_crud):
    """
    Creates and returns a user.
    """
    user_data = UserCreate(
        id=2142,
        username="test_user",
        active_member=True,
        section_head=True,
        roles=["testa", "sgrill"]
    )

    user = await user_crud.create(user_data)
    return user


@pytest_asyncio.fixture
async def reservation_service(reservation_service_crud):
    """
    Creates and returns a reservation service.
    """
    reservation_service_data = ReservationServiceCreate(
        name="Game Room",
        alias="game",
        web="https://herna.cool.go.com",
        contact_mail="game@buk.ok.sh.com",
        public=False
    )

    reservation_service = await reservation_service_crud.create(reservation_service_data)
    return reservation_service

# @pytest_asyncio.fixture
# async def authorized_client(client: AsyncClient, user) -> AsyncClient:
#     token = f"fake-token-{uuid.uuid4()}"
#
#     session_cookie = {
#         "oauth_token": {"access_token": "fake-token"},
#         "user_username": user.username
#     }
#     await client.post("/test/set-session", json=session_cookie)
#
#     secret_key = "testsecret"
#     serializer = itsdangerous.URLSafeSerializer(secret_key, salt="starlette.sessions")
#     session_cookie_value = serializer.dumps(session_cookie)
#
#     client.cookies.set("session", session_cookie_value)
#
#     return client
