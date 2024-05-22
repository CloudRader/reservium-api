"""
This module provides fixtures for setting up and tearing down an in-memory database
used for testing CRUD operations on the models. It defines fixtures and functions
to ensure proper handling of the database and UUIDs during the testing process.
"""
from typing import Generator, Dict, Any

import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from core import settings
from db import Base


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
