"""Calendar ORM model and its dependencies."""

from typing import TYPE_CHECKING

from core.models.base_class import Base
from core.models.soft_delete_mixin import SoftDeleteMixin
from core.models.types.rules_type import RulesType
from core.schemas.calendar import Rules
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:  # pragma: no cover
    from core.models.event import Event
    from core.models.mini_service import MiniService
    from core.models.reservation_service import ReservationService


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

    collisions: Mapped[list["Calendar"]] = relationship(
        "Calendar",
        secondary="calendar_collision_association",
        primaryjoin="Calendar.id==CalendarCollisionAssociationTable.calendar_id",
        secondaryjoin="Calendar.id==CalendarCollisionAssociationTable.collides_with_id",
        lazy="selectin",
        back_populates="collisions",
        remote_side="Calendar.id",
    )

    @property
    def collision_ids(self) -> list[str]:
        """Return only the IDs of calendars this one collides with."""
        return [c.id for c in self.collisions or []]
