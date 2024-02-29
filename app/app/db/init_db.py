"""
Modul which includes functions for initializing database.
"""
from db.base_class import Base
from db.session import engine


def init_db() -> None:
    """
    Initialize database. Create tables for all models if they are not created.
    Note, that in database tables may not be created instantly, only after some crud operation.
    """
    # Base class is managed by SQLAlchemy and its type is assigned by as_declarative decorator
    # pylint: disable=no-member
    Base.metadata.create_all(bind=engine)
    # pylint: enable=no-member
