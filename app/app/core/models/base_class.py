"""
Module with SQLAlchemy base class used to create other models from this Base class.
"""

from uuid import UUID, uuid4

from core import settings
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID as pgUUID  # noqa: N811
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    Base class of all ORM mapped models.
    """

    __abstract__ = True

    metadata = MetaData(naming_convention=settings.DB.NAMING_CONVENTION)

    id: Mapped[UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, default=uuid4,
    )

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805 # declared_attr uses class method style
        return cls.__name__.lower()
