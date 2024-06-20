"""
Module which includes classes and methods responsible for connection to database.
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from core import settings

DATABASE_URI = str(settings.POSTGRES_DATABASE_URI)
engine = create_engine(DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Generates database connections provided by Session class.
    :return: yields database session which will be automatically closed after request is satisfied.
    """
    with SessionLocal() as db:
        yield db
