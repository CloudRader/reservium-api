"""Calendar ORM model and its dependencies."""

import json
from typing import TYPE_CHECKING, Any

from core.models.base_class import Base
from core.models.soft_delete_mixin import SoftDeleteMixin
from core.schemas.calendar import Rules
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TEXT, TypeDecorator

if TYPE_CHECKING:
    from core.models.event import Event
    from core.models.mini_service import MiniService
    from core.models.reservation_service import ReservationService


class RulesType(TypeDecorator):
    """
    Custom SQLAlchemy type for serializing and deserializing the `Rules` Pydantic model.

    This type handles conversion of `Rules` objects to and from JSON for database storage.
    """

    impl = TEXT

    @property
    def python_type(self) -> type[Any]:
        return Rules

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value, dialect):  # noqa: ARG002
        if value is None:
            return None
        if isinstance(value, dict):
            value = Rules(**value)
        return json.dumps(value.model_dump())

    def process_result_value(self, value, dialect):  # noqa: ARG002
        if value is None:
            return None
        return Rules.model_validate_json(value)

    def process_literal_param(self, value, dialect):  # noqa: ARG002
        if value is None:
            return None
        if isinstance(value, dict):
            value = Rules(**value)
        return json.dumps(value.model_dump())

    def copy(self, **kw):  # noqa: ARG002
        return RulesType(self.impl)


class Calendar(Base, SoftDeleteMixin):
    """Calendar model to create and manipulate user entity in the database."""

    id: Mapped[str] = mapped_column(primary_key=True)
    reservation_type: Mapped[str] = mapped_column(unique=True, nullable=False)
    color: Mapped[str] = mapped_column(default="#05baf5", nullable=False)
    max_people: Mapped[int] = mapped_column(default=0, nullable=False)
    more_than_max_people_with_permission: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )
    collision_with_itself: Mapped[bool] = mapped_column(default=False, nullable=False)
    collision_with_calendar: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    club_member_rules: Mapped[Rules] = mapped_column(RulesType(), nullable=True)
    active_member_rules: Mapped[Rules] = mapped_column(RulesType(), nullable=False)
    manager_rules: Mapped[Rules] = mapped_column(RulesType(), nullable=False)

    reservation_service_id: Mapped[str] = mapped_column(ForeignKey("reservation_service.id"))

    reservation_service: Mapped["ReservationService"] = relationship(
        back_populates="calendars",
    )
    events: Mapped[list["Event"]] = relationship(
        back_populates="calendar",
        lazy="selectin",
    )
    mini_services: Mapped[list["MiniService"]] = relationship(
        secondary="calendar_mini_service_association",
        back_populates="calendars",
        lazy="selectin",
    )
