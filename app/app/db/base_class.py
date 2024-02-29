"""
Module with SQLAlchemy base class used to create other models from this Base class.
"""
from uuid import UUID

from sqlalchemy.orm import as_declarative, declared_attr


# Base class is managed by SQLAlchemy and doesn't need more public methods
# pylint: disable=too-few-public-methods
@as_declarative()
class Base:
    """
    Base class of all ORM mapped models.
    """
    uuid: UUID  # typehint for SQLAlchemy for every id attribute
    __name__: str

    # declared_attr decorator already treats method as a class method and requires to use cls
    # pylint: disable=no-self-argument
    # Generate __tablename__ automatically
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    # pylint: enable=no-self-argument
# pyling: enable=too-few-public-methods
