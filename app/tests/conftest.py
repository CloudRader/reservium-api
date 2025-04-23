"""
Fixtures for setting up and tearing down the test PostgreSQL database using testcontainers.
Provides async sessions for tests, with schema management.
"""
from urllib.parse import urlparse, urlunparse

import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from db import Base


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


class TestDatabaseSession:
    """
    Manages async engine and session for PostgreSQL test container.
    """

    def __init__(self, container: PostgresContainer):
        raw_url = str(container.get_connection_url())
        parsed_url = urlparse(raw_url)

        # Replace scheme to use asyncpg driver
        async_url = urlunparse(parsed_url._replace(scheme="postgresql+asyncpg"))

        self.engine = create_async_engine(
            async_url,
            echo=True,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    # @asynccontextmanager
    # async def session_dependency(self):
    #     """
    #     Yields an async DB session.
    #     """
    #     async with self.session_factory() as session:
    #         yield session
    async def get_session(self):
        """
        Opens and returns an async session.
        """
        return self.session_factory()

    async def create_schema(self):
        """
        Creates all tables from metadata.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_and_create_all(self):
        """
        Drops and recreates all tables from metadata.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="session")
async def pg_container():
    """
    Starts and yields a PostgreSQL container for the test session.
    """
    container = PostgresContainer("postgres:15")
    container.start()
    try:
        yield container
    finally:
        container.stop()


@pytest_asyncio.fixture(scope="function")
async def async_session(pg_container):
    """
    Provides a fresh database session for each test (with schema reset).
    """
    db_session = TestDatabaseSession(pg_container)
    await db_session.drop_and_create_all()

    session = await db_session.get_session()
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def shared_session(pg_container):
    """
    Provides a shared schema for all tests, but new session each time.
    """
    db_session = TestDatabaseSession(pg_container)
    await db_session.create_schema()

    session = await db_session.get_session()
    try:
        yield session
    finally:
        await session.close()
