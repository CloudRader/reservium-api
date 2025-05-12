"""
This module provides fixtures for test services
"""
import pytest
import pytest_asyncio

from models.event import EventState
from models.reservation_service import ReservationService
from schemas import UserIS, LimitObject, Role, Service, ServiceValidity, \
    ReservationServiceCreate, User, UserCreate, RegistrationFormCreate, \
    MiniServiceCreate, MiniService, CalendarCreate, Calendar, Rules, \
    Zone, Room, InformationFromIS, EventCreate, Event


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest

# pylint: disable=duplicate-code
# reason: needed for testing; similar conftests are intentionally
# separated by the model they belong to

# pylint: disable=import-outside-toplevel
# reason: circular import issue


@pytest.fixture()
def service_user(async_session):
    """
    Return UserService.
    """
    from services import UserService
    return UserService(db=async_session)


@pytest.fixture()
def service_reservation_service(async_session):
    """
    Return ReservationServiceService.
    """
    from services import ReservationServiceService
    return ReservationServiceService(db=async_session)


@pytest.fixture()
def service_mini_service(async_session):
    """
    Return MiniServiceService.
    """
    from services import MiniServiceService
    return MiniServiceService(db=async_session)


@pytest.fixture()
def service_calendar(async_session):
    """
    Return MiniServiceService.
    """
    from services import CalendarService
    return CalendarService(db=async_session)


@pytest.fixture()
def service_event(async_session):
    """
    Return EventService.
    """
    from services import EventService
    return EventService(db=async_session)


@pytest.fixture()
def service_email():
    """
    Return EmailService.
    """
    from services import EmailService
    return EmailService()


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


@pytest.fixture()
def roles_data_from_is(limit_data_from_is) -> list[Role]:
    """
    Return new Role schema.
    """
    return [Role(
        role="service_admin",
        name="Service admin",
        description="neco",
        limit="Grillcentrum, Klubovna, Studovna",
        limit_objects=[limit_data_from_is],
    )]


@pytest.fixture()
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


@pytest.fixture()
def services_data_from_is(
        service_data_from_is
) -> list[ServiceValidity]:
    """
    Return new ServiceValidity schema.
    """
    return [ServiceValidity(
        from_="2024-02-12",
        to="2024-08-31",
        note="Zaklad",
        service=service_data_from_is,
        usetype="free"
    )]


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


@pytest.fixture()
def data_from_is(user_data_from_is,
                 room_data_from_is,
                 services_data_from_is) -> InformationFromIS:
    """
    Return new InformationFromIS schema.
    """
    return InformationFromIS(
        user=user_data_from_is,
        room=room_data_from_is,
        services=services_data_from_is
    )


@pytest.fixture()
def event_create_form() -> EventCreate:
    """
    Return creating Event schema.
    """
    return EventCreate(
        start_datetime="2025-04-28T12:30",
        end_datetime="2025-04-29T21:00",
        purpose="Birthday party test",
        guests=7,
        reservation_type="Game Room",
        email="user_mail_test@gmail.com",
        additional_services=[],
    )


@pytest.fixture()
def server_create_user(service_user,
                       user_data_from_is,
                       roles_data_from_is,
                       services_data_from_is,
                       room_data_from_is):
    """
    Return server creating user.
    """
    return service_user.create_user(
        user_data_from_is,
        roles_data_from_is,
        services_data_from_is,
        room_data_from_is
    )


@pytest_asyncio.fixture()
async def user(service_user) -> User:
    """
    Return user object in db.
    """
    return await service_user.create(UserCreate(
        id=9897,
        username="gaga_bakalara",
        full_name="=Gagir Bakalar",
        room_number="54875",
        active_member=True,
        section_head=True,
        roles=["game", "stud", "club"],
    ))


@pytest_asyncio.fixture()
async def event(
        service_event,
        event_create_form,
        user, calendar
) -> Event:
    """
    Return event object in db.
    """
    event_create_form.reservation_type=calendar.id
    return await service_event.create_event(
        event_create=event_create_form,
        user=user,
        event_state=EventState.CONFIRMED,
        event_id="w67adfiwfawf"
    )


@pytest_asyncio.fixture()
async def user_not_head(service_user) -> User:
    """
    Return user without head permission object in db.
    """
    return await service_user.create(UserCreate(
        id=5045,
        username="not_head_user",
        full_name="=wuiyaf Yhwvf",
        room_number="43643",
        active_member=False,
        section_head=False,
        roles=[],
    ))


@pytest.fixture()
def reservation_service_create() -> ReservationServiceCreate:
    """
    Return ReservationServiceCreate schema.
    """
    return ReservationServiceCreate(
        name="Game Room",
        alias="game",
        web="https://herna.cool.go.com",
        contact_mail="game@buk.ok.sh.com",
        public=False
    )


@pytest_asyncio.fixture()
async def reservation_service(service_reservation_service,
                              reservation_service_create,
                              user) -> ReservationService:
    """
    Return reservation service object in db.
    """
    return await service_reservation_service.create_reservation_service(
        reservation_service_create, user
    )


@pytest.fixture()
def mini_service_create(reservation_service) -> MiniServiceCreate:
    """
    Return MiniServiceCreate schema.
    """
    return MiniServiceCreate(
        name="Bar",
        reservation_service_id=reservation_service.id,
    )


@pytest_asyncio.fixture()
async def mini_service(service_mini_service,
                       mini_service_create,
                       user) -> MiniService:
    """
    Return mini service object in db.
    """
    return await service_mini_service.create_mini_service(
        mini_service_create, user
    )


@pytest.fixture
def rules_schema() -> Rules:
    """
    Return rules schemas.
    """
    return Rules(
        night_time=False,
        reservation_without_permission=False,
        max_reservation_hours=32,
        in_advance_hours=36,
        in_advance_minutes=0,
        in_prior_days=14
    )


@pytest.fixture(scope="module")
def calendar_rules_create() -> Rules:
    """
    Return rules schemas.
    """
    return Rules(
        night_time=False,
        reservation_without_permission=True,
        max_reservation_hours=32,
        in_advance_hours=36,
        in_advance_minutes=0,
        in_prior_days=60
    )


@pytest.fixture()
def calendar_create(reservation_service,
                    calendar_rules_create) -> CalendarCreate:
    """
    Return CalendarCreate schema.
    """
    return CalendarCreate(
        id="service.cal.test@test.zc",
        reservation_type="Galambula",
        color="#kg9032",
        max_people=8,
        more_than_max_people_with_permission=True,
        collision_with_itself=True,
        collision_with_calendar=[],
        club_member_rules=calendar_rules_create,
        active_member_rules=calendar_rules_create,
        manager_rules=calendar_rules_create,
        reservation_service_id=reservation_service.id,
        mini_services=[]
    )


@pytest_asyncio.fixture()
async def calendar(service_calendar,
                   calendar_create,
                   user) -> Calendar:
    """
    Return calendar object in db.
    """
    return await service_calendar.create_calendar(
        calendar_create, user
    )


@pytest.fixture()
def registration_form_create() -> RegistrationFormCreate:
    """
    Return RegistrationFormCreate schema.
    """
    return RegistrationFormCreate(
        event_name="Birthday Party",
        guests=15,
        event_start="2025-04-25T15:11",
        event_end="2025-04-25T20:11",
        email="some.guest@gcloud.com",
        organizers="Dan Ababa, Greg Aloda",
        space="Club Room",
        other_space=["Study Room", "Grillcentrum"],
        manager_contact_mail="this.space@buk.cvut.cz",
    )
