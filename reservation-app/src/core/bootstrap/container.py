"""Dependency injection container for the application services, repositories, and providers."""

from application.ports.providers.calendar import CalendarProvider
from application.ports.providers.identity import IdentityProvider
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
from sqlalchemy.ext.asyncio import AsyncSession


class Container:
    """
    Dependency injection container class.

    Responsible for initializing and providing application services,
    repositories, and external providers.
    """

    def __init__(
        self,
        db: AsyncSession,
        calendar_provider: CalendarProvider,
        identity_provider: IdentityProvider,
        email_service: EmailService,
    ):

        # Repositories
        self._calendar_repository = SQLAlchemyCalendarRepository(db)
        self._event_repository = SQLAlchemyEventRepository(db)
        self._mini_service_repository = SQLAlchemyMiniServiceRepository(db)
        self._reservation_service_repository = SQLAlchemyReservationServiceRepository(db)
        self._user_repository = SQLAlchemyUserRepository(db)

        # Providers
        self._calendar_provider = calendar_provider
        self._identity_provider = identity_provider
        self._email_service = email_service

        # Services
        self._reservation_service_service = ReservationServiceService(
            self._reservation_service_repository,
        )
        self._mini_service_service = MiniServiceService(
            self._mini_service_repository,
            self._reservation_service_service,
        )
        self._calendar_service = CalendarService(
            self._calendar_repository,
            self._reservation_service_service,
            self._mini_service_service,
            self._calendar_provider,
        )
        self._event_service = EventService(
            self._event_repository,
            self._reservation_service_service,
            self._calendar_service,
            self._user_repository,
            self._calendar_provider,
            self._email_service,
        )
        self._user_service = UserService(
            self._user_repository,
            self._reservation_service_repository,
        )

    # =============== Services ===============
    @property
    def calendar_service(self) -> CalendarService:
        return self._calendar_service

    @property
    def event_service(self) -> EventService:
        return self._event_service

    @property
    def mini_service_service(self) -> MiniServiceService:
        return self._mini_service_service

    @property
    def reservation_service_service(self) -> ReservationServiceService:
        return self._reservation_service_service

    @property
    def user_service(self) -> UserService:
        return self._user_service
