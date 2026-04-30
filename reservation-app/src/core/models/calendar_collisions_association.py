"""Calendar-to-Calendar ORM model association for collisions."""

from core.models.base import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class CalendarCollisionAssociation(Base):
    """
    Association table for self-referential many-to-many.

    Relationship between Calendar instances that collide with each other.
    """

    __table_args__ = (UniqueConstraint("calendar_id", "collides_with_id"),)

    calendar_id: Mapped[str] = mapped_column(ForeignKey("calendars.id", ondelete="CASCADE"))
    collides_with_id: Mapped[str] = mapped_column(ForeignKey("calendars.id", ondelete="CASCADE"))
