"""Calendar nad Mini Service ORM model association."""

from uuid import UUID

from core.models.base_class import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class CalendarMiniServiceAssociationTable(Base):
    """Association table for many-to-many relationship between Calendar and MiniService."""

    __tablename__ = "calendar_mini_service_association"
    __table_args__ = (UniqueConstraint("calendar_id", "mini_service_id"),)

    calendar_id: Mapped[str] = mapped_column(ForeignKey("calendar.id"))
    mini_service_id: Mapped[UUID] = mapped_column(ForeignKey("mini_service.id"))
