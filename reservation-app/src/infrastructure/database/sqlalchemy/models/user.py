"""User ORM model and its dependencies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:  # pragma: no cover
    from infrastructure.database.sqlalchemy.models.event import Event


class User(Base):
    """User model to create and manipulate user entity in the database."""

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    provider_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    active_member: Mapped[bool] = mapped_column(
        unique=False,
        nullable=False,
        default=False,
    )
    roles: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        unique=False,
        nullable=True,
    )

    events: Mapped[list[Event]] = relationship(back_populates="user", lazy="selectin")
