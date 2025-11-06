"""User ORM model and its dependencies."""

from typing import TYPE_CHECKING

from core.models.base_class import Base
from core.models.soft_delete_mixin import SoftDeleteMixin
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:  # pragma: no cover
    from core.models.event import Event


class User(Base, SoftDeleteMixin):
    """User model to create and manipulate user entity in the database."""

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    active_member: Mapped[bool] = mapped_column(
        unique=False,
        nullable=False,
        default=False,
    )
    section_head: Mapped[bool] = mapped_column(
        unique=False,
        nullable=False,
        default=False,
    )
    roles: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        unique=False,
        nullable=True,
    )

    events: Mapped[list["Event"]] = relationship(back_populates="user", lazy="selectin")
