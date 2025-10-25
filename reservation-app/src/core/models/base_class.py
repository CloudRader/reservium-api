"""Module with SQLAlchemy base class used to create other models from this Base class."""

from uuid import uuid4

from core import settings
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Base class of all ORM mapped models."""

    __abstract__ = True

    metadata = MetaData(naming_convention=settings.DB.NAMING_CONVENTION)

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: uuid4().hex,
    )

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:  # noqa: N805 # declared_attr uses class method style
        """Generate a table name based on the lowercase class name."""
        return cls.__name__.lower()
