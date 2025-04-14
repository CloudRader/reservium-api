"""
Module which includes classes and methods responsible for connection to database.
"""
from typing import AsyncGenerator
from asyncio import current_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    async_scoped_session, AsyncSession
from core import settings


class DatabaseSession:
    """
    Manages the creation and handling of asynchronous database sessions.

    This class provides methods to create both regular and scoped database
    sessions. A regular session is used for simple operations, while a scoped
    session ensures that multiple database operations share the same session
    within a specific scope (e.g., a request cycle).

    It utilizes SQLAlchemy’s `async_sessionmaker` and `async_scoped_session` to
    handle sessions in an async context.
    """

    def __init__(self):
        self.engine = create_async_engine(
            url=str(settings.POSTGRES_DATABASE_URI),
            pool_pre_ping=True
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    def get_scoped_session(self):
        """
        Returns a scoped asynchronous session tied to the current task.

        Uses `async_scoped_session` to create a session that is scoped to the
        current async task, ensuring that all database operations within the
        scope share the same session.
        """
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Yields an asynchronous database session.
        The session is automatically closed after use.
        """
        async with self.session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    async def scoped_session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Yields a scoped asynchronous session, tied to the current task.
        The session is closed after the request completes.
        """
        session = self.get_scoped_session()
        try:
            yield session
        finally:
            await session.close()


db_session = DatabaseSession()
