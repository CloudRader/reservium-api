"""Module which includes classes and methods responsible for connection to database."""

import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)


def create_engine(
    url: str,
    *,
    echo: bool = False,
    echo_pool: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_pre_ping: bool = True,
    pool_recycle: int = 3600,
) -> AsyncEngine:
    """
    Create an asynchronous SQLAlchemy engine.

    :param url: Database connection URL.
    :param echo: If True, SQL statements are logged.
    :param echo_pool: If True, connection pool events are logged.
    :param pool_size: Number of connections to keep in the pool.
    :param max_overflow: Max connections allowed beyond pool_size.
    :param pool_pre_ping: If True, the pool will ping connections before using them.
    :param pool_recycle: Time in seconds before recycling connections.
    :return: An AsyncEngine instance.
    """
    return create_async_engine(
        url=url,
        echo=echo,
        echo_pool=echo_pool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        pool_recycle=pool_recycle,
    )


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """
    Create an asynchronous sessionmaker bound to the given engine.

    :param engine: The AsyncEngine instance.
    :return: An async_sessionmaker configured for AsyncSession.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
