"""Dishka dependency injection providers for the application."""

from collections.abc import AsyncIterator

from application.ports.providers.calendar import CalendarProvider
from application.ports.providers.email import EmailProvider
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
    EventService,
    MiniServiceService,
    ReservationServiceService,
    UserService,
)
from authlib.integrations.starlette_client import OAuth
from core.config.settings import Settings
from dishka import Provider, Scope, provide
from fastapi_mail import FastMail
from google.oauth2 import service_account
from googleapiclient.discovery import build
from infrastructure.calendar.google.provider import GoogleCalendarProvider
from infrastructure.database.sqlalchemy.repositories import (
    SQLAlchemyCalendarRepository,
    SQLAlchemyEventRepository,
    SQLAlchemyMiniServiceRepository,
    SQLAlchemyReservationServiceRepository,
    SQLAlchemyUserRepository,
)
from infrastructure.database.sqlalchemy.session import create_engine, create_session_factory
from infrastructure.email.provider import FastEmailProvider
from infrastructure.identity.openid.provider import OpenIdProvider
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)


class SettingsProvider(Provider):
    """Provides application settings."""

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        """Provide the Settings instance."""
        return Settings()


class DatabaseProvider(Provider):
    """Provides database-related dependencies, such as session factory and sessions."""

    @provide(scope=Scope.APP)
    async def get_engine(self, settings: Settings) -> AsyncIterator[AsyncEngine]:
        """Provide a single AsyncEngine for the app's lifetime; disposed on shutdown."""
        engine = create_engine(
            url=settings.database.postgres_database_uri,
            echo=settings.database.echo,
            echo_pool=settings.database.echo_pool,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
        )
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    def get_session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        """Provide the sessionmaker, built once per app lifetime."""
        return create_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        """Provide a fresh AsyncSession per request; closed automatically after."""
        async with factory() as session:
            yield session


class RepositoryProvider(Provider):
    """Provides repository implementations."""

    @provide(scope=Scope.REQUEST)
    def get_calendar_repository(self, session: AsyncSession) -> CalendarRepository:
        """Provide a CalendarRepository implementation."""
        return SQLAlchemyCalendarRepository(db=session)

    @provide(scope=Scope.REQUEST)
    def get_event_repository(self, session: AsyncSession) -> EventRepository:
        """Provide an EventRepository implementation."""
        return SQLAlchemyEventRepository(db=session)

    @provide(scope=Scope.REQUEST)
    def get_mini_service_repository(self, session: AsyncSession) -> MiniServiceRepository:
        """Provide a MiniServiceRepository implementation."""
        return SQLAlchemyMiniServiceRepository(db=session)

    @provide(scope=Scope.REQUEST)
    def get_reservation_service_repository(
        self, session: AsyncSession
    ) -> ReservationServiceRepository:
        """Provide a ReservationServiceRepository implementation."""
        return SQLAlchemyReservationServiceRepository(db=session)

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSession) -> UserRepository:
        """Provide a UserRepository implementation."""
        return SQLAlchemyUserRepository(db=session)


class ServiceProvider(Provider):
    """Provides application services."""

    @provide(scope=Scope.REQUEST)
    def get_calendar_service(
        self,
        calendar_repository: CalendarRepository,
        reservation_service_service: ReservationServiceService,
        mini_service_service: MiniServiceService,
        calendar_provider: CalendarProvider,
    ) -> CalendarService:
        """Provide a CalendarService instance."""
        return CalendarService(
            calendar_repository=calendar_repository,
            reservation_service_service=reservation_service_service,
            mini_service_service=mini_service_service,
            calendar_provider=calendar_provider,
        )

    @provide(scope=Scope.REQUEST)
    def get_event_service(
        self,
        event_repository: EventRepository,
        reservation_service_service: ReservationServiceService,
        calendar_service: CalendarService,
        user_repository: UserRepository,
        calendar_provider: CalendarProvider,
        email_provider: EmailProvider,
    ) -> EventService:
        """Provide an EventService instance."""
        return EventService(
            event_repository=event_repository,
            reservation_service_service=reservation_service_service,
            calendar_service=calendar_service,
            user_repository=user_repository,
            calendar_provider=calendar_provider,
            email_provider=email_provider,
        )

    @provide(scope=Scope.REQUEST)
    def get_mini_service_service(
        self,
        mini_service_repository: MiniServiceRepository,
        reservation_service_service: ReservationServiceService,
    ) -> MiniServiceService:
        """Provide a MiniServiceService instance."""
        return MiniServiceService(
            mini_service_repository=mini_service_repository,
            reservation_service_service=reservation_service_service,
        )

    @provide(scope=Scope.REQUEST)
    def get_reservation_service_service(
        self,
        reservation_service_repository: ReservationServiceRepository,
    ) -> ReservationServiceService:
        """Provide a ReservationServiceService instance."""
        return ReservationServiceService(
            reservation_service_repository=reservation_service_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_user_service(
        self,
        user_repository: UserRepository,
        reservation_service_repository: ReservationServiceRepository,
    ) -> UserService:
        """Provide a UserService instance."""
        return UserService(
            user_repository=user_repository,
            reservation_service_repository=reservation_service_repository,
        )


class ExternalProvidersProvider(Provider):
    """Provides external service integrations."""

    @provide(scope=Scope.APP)
    def get_calendar_provider(self, settings: Settings) -> CalendarProvider:
        """Provide a CalendarProvider implementation."""
        credentials = service_account.Credentials.from_service_account_info(
            info=settings.google.info,
            scopes=settings.google.scopes,
        )
        client = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        return GoogleCalendarProvider(
            client=client,
            service_account_email=settings.google.client_email,
            mail_username=settings.mail.username,
        )

    @provide(scope=Scope.APP)
    def get_identity_provider(self, settings: Settings) -> IdentityProvider:
        """Provide an IdentityProvider implementation."""
        oauth = OAuth()
        oauth.register(
            name=settings.openid.client_name,
            client_id=settings.openid.client_id,
            client_secret=settings.openid.client_secret,
            server_metadata_url=settings.openid.metadata_url,
            client_kwargs={"scope": settings.openid.scopes},
        )
        client = oauth.create_client(settings.openid.client_name)
        return OpenIdProvider(
            client=client,
            client_id=settings.openid.client_id,
            client_secret=settings.openid.client_secret.get_secret_value(),
        )

    @provide(scope=Scope.APP)
    def get_email_provider(self, settings: Settings) -> EmailProvider:
        """Provide an EmailProvider implementation."""
        client = FastMail(settings.mail.connection)
        return FastEmailProvider(
            client=client,
            send_facility_manager=settings.mail.sent_dormitory_head,
            facility_manager_email=settings.mail.dormitory_head_email,
            organisation_name=settings.app.organization_name,
        )
