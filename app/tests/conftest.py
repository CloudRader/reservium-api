"""
This module provides fixtures for setting up and tearing down an in-memory database
used for testing CRUD operations on the models. It defines fixtures and functions
to ensure proper handling of the database and UUIDs during the testing process.
Except that other fixture that use in all tests modules
"""
from typing import Generator, Dict, Any

import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from starlette.testclient import TestClient

from core import settings
from db import Base, get_db
from schemas import CalendarCreate, CalendarUpdate, \
    UserCreate, UserUpdate, UserIS, Role, LimitObject, \
    MiniServiceCreate, MiniServiceUpdate, Room, Zone, \
    Service, ServiceValidity, InformationFromIS, EventCreate, User
from services import UserService, CalendarService
from main import app


# Using fixtures as variables is a standard for pytest
# pylint: disable=redefined-outer-name

@pytest.fixture(scope="module")
def db_url() -> tuple[str, Dict[str, Any]]:
    """Get database url.

    return (str, Dict[str, Any]): (database_url, {})
    """
    return settings.TEST_DATABASE_URI, {}


@pytest.fixture(scope="module")
def db_engine(db_url: tuple[str, Dict[str, Any]]) -> Engine:
    """Get database engine.

    :param db_url: Database url format.
    :return Engine: Database engine.
    """
    url, kwargs = db_url
    return create_engine(url, **kwargs)


@pytest.fixture(scope="module")
def db_session_maker(db_engine):
    """
    Provides a session maker for creating database sessions for the in-memory database.
    Sets up and tears down the database schema for each module session.

    :param db_engine: The SQLAlchemy Engine connected to the in-memory database.
    :return: A session maker for making database sessions
    """
    # Base class is managed by SQLAlchemy and its type is assigned by as_declarative decorator
    # pylint: disable=no-member
    Base.metadata.create_all(bind=db_engine)
    session_maker = sessionmaker(bind=db_engine)
    yield session_maker
    Base.metadata.drop_all(bind=db_engine)
    # pylint: enable=no-member


@pytest.fixture()
def db_session(db_session_maker) -> Generator[Session, None, None]:
    """
    Provides database sessions.
    :param db_session_maker: Session maker for creating database sessions
    :return: Session to the database
    """
    with db_session_maker() as db:
        yield db


@pytest.fixture(scope="module")
def client(db_session_maker):
    """
    Return new client for testing api.
    """
    def override_get_db():
        with db_session_maker() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


# Schemas


@pytest.fixture()
def mini_service_create() -> MiniServiceCreate:
    """
    Return new MiniServiceCreate schema.
    """
    return MiniServiceCreate(
        name="Board games",
        service_alias="stud",
    )


@pytest.fixture()
def mini_service_update() -> MiniServiceUpdate:
    """
    Return new MiniServiceUpdate schema.
    """
    return MiniServiceUpdate(
        service_alias="klub",
    )


@pytest.fixture(scope="module")
def rules_json_club_member() -> dict:
    """
    Return rules json object.
    """
    return {
        "night_time": False,
        "reservation_more_24_hours": False,
        "in_advance_hours": 24,
        "in_advance_minutes": 30,
        "in_advance_day": 14
    }


@pytest.fixture(scope="module")
def calendar_create(rules_json_club_member) -> CalendarCreate:
    """
    Return new calendar.
    """
    return CalendarCreate(
        calendar_id="c_f8a87bad9df63841a343835e6c55964349",
        service_alias="stud",
        reservation_type="Study Room",
        event_name="Studovna/Study Room",
        max_people=15,
        collision_with_itself=False,
        collision_with_calendar=[],
        club_member_rules=rules_json_club_member,
        active_member_rules=rules_json_club_member,
        manager_rules=rules_json_club_member,
        mini_services=["Bar", "Consoles", "Games"]
    )


@pytest.fixture()
def calendar_update() -> CalendarUpdate:
    """
    Return new CalendarUpdate schema.
    """
    return CalendarUpdate(
        max_people=10,
    )


@pytest.fixture()
def user_create() -> UserCreate:
    """
    Return new UserCreate schema.
    """
    return UserCreate(
        username="buk_ashi",
        user_token="fh327ygf3yfvs",
        active_member=False,
    )


@pytest.fixture()
def user_update() -> UserUpdate:
    """
    Return new UserUpdate schema.
    """
    return UserUpdate(
        active_member=True,
    )


@pytest.fixture(scope="module")
def zone_data_from_is() -> Zone:
    """
    Return new Zone schema.
    """
    return Zone(
        alias=None,
        id=252,
        name="blok",
        note="cool",
    )


@pytest.fixture(scope="module")
def room_data_from_is(zone_data_from_is) -> Room:
    """
    Return new Room schema.
    """
    return Room(
        door_number="212",
        floor=2,
        id=212,
        name=None,
        zone=zone_data_from_is
    )


@pytest.fixture(scope="module")
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


@pytest.fixture(scope="module")
def limit_data_from_is() -> LimitObject:
    """
    Return new LimitObject schema.
    """
    return LimitObject(
        id=1,
        name="Studovna",
        alias="stud",
        note="Spravuje studovnu",
    )


@pytest.fixture(scope="module")
def role_data_from_is(limit_data_from_is) -> Role:
    """
    Return new Role schema.
    """
    return Role(
        role="service_admin",
        name="Service admin",
        description="neco",
        limit="Grillcentrum, Klubovna, Studovna",
        limit_objects=[limit_data_from_is],
    )


@pytest.fixture(scope="module")
def roles_data_from_is(role_data_from_is) -> list[Role]:
    """
    Return new list[Role] schemas.
    """
    return [role_data_from_is]


@pytest.fixture(scope="module")
def service_data_from_is() -> Service:
    """
    Return new Service schema.
    """
    return Service(
        alias="stud",
        name="Studovna",
        note=None,
        servicetype="free_auto",
        web="buk.cvut.cz"
    )


@pytest.fixture(scope="module")
def service_validity_data_from_is(
        service_data_from_is
) -> ServiceValidity:
    """
    Return new ServiceValidity schema.
    """
    return ServiceValidity(
        from_="2024-02-12",
        to="2024-08-31",
        note="Zaklad",
        service=service_data_from_is,
        usetype="free"
    )


@pytest.fixture(scope="module")
def services_data_from_is(
        service_validity_data_from_is
) -> list[ServiceValidity]:
    """
    Return new list[ServiceValidity] schemas.
    """
    return [service_validity_data_from_is]


@pytest.fixture(scope="module")
def information_data_from_is(
        services_data_from_is,
        room_data_from_is,
        user_data_from_is
) -> InformationFromIS:
    """
    Return new InformationFromIS schemas.
    """
    return InformationFromIS(
        user=user_data_from_is,
        room=room_data_from_is,
        services=services_data_from_is
    )


@pytest.fixture()
def event_create() -> EventCreate:
    """
    Return new EventCreate schemas.
    """
    return EventCreate(
        start_datetime="2024-12-05T10:00:00",
        end_datetime="2024-12-05T23:00:00",
        purpose="Chill",
        guests=5,
        reservation_type="Study Room",
        email="some_test_other_bother@buk.cvut.cz",
        username="kanya_garin",
    )


# Services
@pytest.fixture()
def service_user(db_session) -> UserService:
    """
    Return UserService.
    """
    return UserService(db=db_session)


@pytest.fixture()
def create_user_manager_stud(
        db_session, user_data_from_is, roles_data_from_is
) -> User:
    """
    Return User schema.
    """
    service = UserService(db=db_session)
    return service.create_user(user_data_from_is, roles_data_from_is,
                               "fwafjwafvwaif")


@pytest.fixture()
def service_calendar(db_session) -> CalendarService:
    """
    Return CalendarService.
    """
    return CalendarService(db=db_session)
