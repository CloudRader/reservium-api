"""Event ORM model and its dependencies."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from core.models.base_class import Base
from core.models.soft_delete_mixin import SoftDeleteMixin
from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:  # pragma: no cover
    from core.models.calendar import Calendar
    from core.models.user import User


class EventState(Enum):
    """
    State of the event.

    - **not_approved** - The event has been created but not yet approved.
    - **update_request** - A user has requested changes to the event.
    - **confirmed** - The event is confirmed.
    - **canceled** - The event was previously scheduled but has been canceled.
    """

    NOT_APPROVED = "not_approved"
    UPDATE_REQUESTED = "update_requested"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"


class Event(Base, SoftDeleteMixin):
    """Event model to create and manipulate event entity in the database."""

    id: Mapped[str] = mapped_column(primary_key=True)

    reservation_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reservation_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    requested_reservation_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    requested_reservation_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    purpose: Mapped[str] = mapped_column(nullable=False)
    guests: Mapped[int] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    event_state: Mapped[EventState] = mapped_column(
        SQLAlchemyEnum(EventState, name="event_state_enum"),
        nullable=False,
        default=EventState.NOT_APPROVED,
        server_default=text("'NOT_APPROVED'"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    calendar_id: Mapped[str] = mapped_column(ForeignKey("calendar.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="events")
    calendar: Mapped["Calendar"] = relationship(back_populates="events")
    additional_services: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
