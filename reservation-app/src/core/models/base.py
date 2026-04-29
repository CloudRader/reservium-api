"""Module with SQLAlchemy base class used to create other models from this Base class."""

from datetime import datetime
from uuid import uuid4

from common import get_utc_now, snake_case
from core import settings
from core.models.soft_delete_mixin import SoftDeleteMixin
from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase, SoftDeleteMixin):
    """Base class of all ORM mapped models."""

    __abstract__ = True

    metadata = MetaData(naming_convention=settings.DB.NAMING_CONVENTION)

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: uuid4().hex,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=get_utc_now,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=get_utc_now,
        server_onupdate=func.now(),
    )

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:  # noqa: N805 # declared_attr uses class method style
        """Generate a table name based on the lowercase class name."""
        return f"{snake_case(cls.__name__)}s"
