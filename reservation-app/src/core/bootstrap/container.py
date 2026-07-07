"""Dependency injection container for the application services, repositories, and providers."""

from application.ports.providers.calendar import CalendarProvider
from application.ports.providers.identity import IdentityProvider
from application.ports.repositories import (
    CalendarRepository,
    EventRepository,
    MiniServiceRepository,
    ReservationServiceRepository,
    UserRepository,
)
from application.services import (
    CalendarService,
    EmailService,
    EventService,
    MiniServiceService,
    ReservationServiceService,
    UserService,
)
from infrastructure.database.sqlalchemy.repositories import (
    SQLAlchemyCalendarRepository,
    SQLAlchemyEventRepository,
    SQLAlchemyMiniServiceRepository,
    SQLAlchemyReservationServiceRepository,
    SQLAlchemyUserRepository,
)
from infrastructure.google.google_calendar_services import GoogleCalendarProvider
from infrastructure.openid import OpenIdProvider
from sqlalchemy.ext.asyncio import AsyncSession


class Container:
    """
    Dependency injection container class.

    Responsible for initializing and providing application services,
    repositories, and external providers.
    """

    def __init__(self, db: AsyncSession):

        # Repositories
        self._calendar_repository = SQLAlchemyCalendarRepository(db)
        self._event_repository = SQLAlchemyEventRepository(db)
        self._mini_service_repository = SQLAlchemyMiniServiceRepository(db)
        self._reservation_service_repository = SQLAlchemyReservationServiceRepository(db)
        self._user_repository = SQLAlchemyUserRepository(db)

        # Providers
        self._calendar_provider = GoogleCalendarProvider()
        self._identity_provider = OpenIdProvider()

        # Services
        self._reservation_service_service = ReservationServiceService(
            self._reservation_service_repository,
        )
        self._mini_service_service = MiniServiceService(
            self._mini_service_repository,
            self._reservation_service_service,
        )
        self._email_service = EmailService()
        self._calendar_service = CalendarService(
            self._calendar_repository,
            self._reservation_service_service,
            self._mini_service_service,
            self._calendar_provider,
        )
        self._event_service = EventService(
            event_repository=self._event_repository,
            reservation_service_service=self._reservation_service_service,
            calendar_service=self._calendar_service,
            user_repository=self._user_repository,
            calendar_provider=self._calendar_provider,
            email_service=self._email_service,
        )

    # =============== Repositories ===============
    def calendar_repository(self) -> CalendarRepository:
        return self._calendar_repository

    def event_repository(self) -> EventRepository:
        return self._event_repository

    def mini_service_repository(self) -> MiniServiceRepository:
        return self._mini_service_repository

    def reservation_service_repository(self) -> ReservationServiceRepository:
        return self._reservation_service_repository

    def user_repository(self) -> UserRepository:
        return self._user_repository

    # =============== Providers ===============
    def google_provider(self) -> CalendarProvider:
        return self._calendar_provider

    def openid_provider(self) -> IdentityProvider:
        return self._identity_provider

    # =============== Services ===============
    def calendar_service(self) -> CalendarService:
        return CalendarService(
            self._calendar_repository,
            self._reservation_service_service,
            self._mini_service_service,
            self._calendar_provider,
        )

    def event_service(self) -> EventService:
        return EventService(
            self._event_repository,
            self._reservation_service_service,
            self._calendar_service,
            self._user_repository,
            self._calendar_provider,
            self._email_service,
        )

    def mini_service_service(self) -> MiniServiceService:
        return MiniServiceService(
            self._mini_service_repository,
            self._reservation_service_service,
        )

    def reservation_service_service(self) -> ReservationServiceService:
        return ReservationServiceService(self._reservation_service_repository)

    def user_service(self) -> UserService:
        return UserService(
            self._user_repository,
            self._reservation_service_repository,
        )
