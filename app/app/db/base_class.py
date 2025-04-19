"""
Module with SQLAlchemy base class used to create other models from this Base class.
"""
from uuid import UUID, uuid4

from sqlalchemy.orm import declared_attr, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as pgUUID


# Base class is managed by SQLAlchemy and doesn't need more public methods
# pylint: disable=too-few-public-methods
# @as_declarative()
class Base(DeclarativeBase):
    """
    Base class of all ORM mapped models.
    """
    __abstract__ = True

    id: Mapped[UUID] =  mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid4)

    # declared_attr decorator already treats method as a class method and requires to use cls
    # pylint: disable=no-self-argument
    # Generate __tablename__ automatically
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    # pylint: enable=no-self-argument
# pyling: enable=too-few-public-methods
