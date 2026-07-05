"""Calendar ORM model and its dependencies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from domain.models.base import Base
from domain.models.types.rules_type import RulesType
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:  # pragma: no cover
    from api.schemas.calendar import Rules
    from domain.models.event import Event
    from domain.models.mini_service import MiniService
    from domain.models.reservation_service import ReservationService
else:
    Rules = Any


class Calendar(Base):
    """Calendar model to create and manipulate user entity in the database."""

    reservation_type: Mapped[str] = mapped_column(unique=True, nullable=False)
    color: Mapped[str] = mapped_column(default="#05baf5", nullable=False)
    max_people: Mapped[int] = mapped_column(default=0, nullable=False)
    more_than_max_people_with_permission: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )
    collision_with_itself: Mapped[bool] = mapped_column(default=False, nullable=False)

    club_member_rules: Mapped[Rules] = mapped_column(RulesType(), nullable=True)
    active_member_rules: Mapped[Rules] = mapped_column(RulesType(), nullable=False)
    manager_rules: Mapped[Rules] = mapped_column(RulesType(), nullable=False)

    provider_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)

    reservation_service_id: Mapped[UUID] = mapped_column(ForeignKey("reservation_services.id"))

    reservation_service: Mapped[ReservationService] = relationship(
        back_populates="calendars",
    )
    events: Mapped[list[Event]] = relationship(
        back_populates="calendar",
        lazy="selectin",
    )
    mini_services: Mapped[list[MiniService]] = relationship(
        secondary="calendar_mini_service_associations",
        back_populates="calendars",
        lazy="selectin",
    )

    collisions: Mapped[list[Calendar]] = relationship(
        "Calendar",
        secondary="calendar_collision_associations",
        primaryjoin="Calendar.id==CalendarCollisionAssociation.calendar_id",
        secondaryjoin="Calendar.id==CalendarCollisionAssociation.collides_with_id",
        lazy="selectin",
        back_populates="collisions",
        remote_side="Calendar.id",
    )

    @property
    def collision_ids(self) -> list[str]:
        """Return only the IDs of calendars this one collides with."""
        return [c.id for c in self.collisions or []]
