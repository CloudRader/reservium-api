"""Calendar nad Mini Service ORM model association."""

from core.models.base import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class CalendarMiniServiceAssociation(Base):
    """Association table for many-to-many relationship between Calendar and MiniService."""

    __table_args__ = (UniqueConstraint("calendar_id", "mini_service_id"),)

    calendar_id: Mapped[str] = mapped_column(ForeignKey("calendars.id"))
    mini_service_id: Mapped[str] = mapped_column(ForeignKey("mini_services.id"))
