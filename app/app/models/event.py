"""
Event ORM model and its dependencies.
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Enum as SQLAlchemyEnum, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.base_class import Base
from models.soft_delete_mixin import SoftDeleteMixin

if TYPE_CHECKING:
    from models.user import User
    from models.calendar import Calendar


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


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
# pylint: disable=unsubscriptable-object
# reason: Custom SQLAlchemy type, based on TypeDecorator.
class Event(Base, SoftDeleteMixin):
    """
    Event model to create and manipulate event entity in the database.
    """

    id: Mapped[str] = mapped_column(primary_key=True)
    purpose: Mapped[str] = mapped_column(nullable=False)
    guests: Mapped[int] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(nullable=False)
    event_state: Mapped[EventState] = mapped_column(
        SQLAlchemyEnum(EventState, name="event_state_enum"),
        nullable=False,
        default=EventState.NOT_APPROVED,
        server_default=text("'NOT_APPROVED'")
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"),
                                         nullable=False)
    calendar_id: Mapped[str] = mapped_column(ForeignKey("calendar.id"),
                                             nullable=False)

    user: Mapped["User"] = relationship(
        back_populates="events")
    calendar: Mapped["Calendar"] = relationship(
        back_populates="events")
    additional_services: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

# pylint: enable=too-few-public-methods
