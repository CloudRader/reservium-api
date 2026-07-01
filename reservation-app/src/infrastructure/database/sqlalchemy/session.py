"""Module which includes classes and methods responsible for connection to database."""

import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from core import settings
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)


class DatabaseSession:
    """
    Asynchronous database session manager using SQLAlchemy.

    This class handles the creation of an asynchronous database engine and
    provides an `async_sessionmaker` factory for producing `AsyncSession` objects.
    It allows consuming code to acquire database sessions in an async context
    using `async with`, and ensures proper cleanup.
    """

    def __init__(
        self,
        url: str,
        *,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ):
        """
        Initialize the database engine and session factory.

        :param: url (str): Database connection URL.
        :param: echo (bool): If True, SQLAlchemy will log all SQL statements.
        :param: echo_pool (bool): If True, SQLAlchemy will log connection pool events.
        :param: pool_size (int): Number of connections to keep in the pool.
        :param: max_overflow (int): Maximum number of connections to allow beyond pool_size.
        """
        self.engine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """
        Dispose of the database engine and release all connections.

        This should be called when shutting down the application to cleanly
        close the connection pool.
        """
        await self.engine.dispose()
        logger.info("Database engine disposed")

    async def session_getter(self) -> AsyncGenerator[AsyncSession]:
        """
        Yield an asynchronous database session.

        The session is automatically closed after use.
        """
        async with self.session_factory() as session:
            yield session


db_session = DatabaseSession(
    url=str(settings.DB.POSTGRES_DATABASE_URI),
    echo=settings.DB.ECHO,
    echo_pool=settings.DB.ECHO_POOL,
    pool_size=settings.DB.POOL_SIZE,
    max_overflow=settings.DB.MAX_OVERFLOW,
)

AsyncSessionDep = Annotated[AsyncSession, Depends(db_session.session_getter)]
