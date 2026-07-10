"""Dishka dependency injection providers for the application."""

from collections.abc import AsyncIterator

from application.ports.repositories import (
    CalendarRepository,
    EventRepository,
    MiniServiceRepository,
    ReservationServiceRepository,
    UserRepository,
)
from core.config.settings import Settings
from dishka import Provider, Scope, provide
from infrastructure.database.sqlalchemy.repositories import (
    SQLAlchemyCalendarRepository,
    SQLAlchemyEventRepository,
    SQLAlchemyMiniServiceRepository,
    SQLAlchemyReservationServiceRepository,
    SQLAlchemyUserRepository,
)
from infrastructure.database.sqlalchemy.session import create_engine, create_session_factory
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)


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
