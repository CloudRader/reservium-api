"""
Calendar nad Mini Service ORM model association.
"""

from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from db.base_class import Base


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
# pylint: disable=unsubscriptable-object
# reason: Custom SQLAlchemy type, based on TypeDecorator.
class CalendarMiniServiceAssociationTable(Base):
    """
    Association table for many-to-many relationship between Calendar and MiniService.
    """

    __tablename__ = "calendar_mini_service_association"
    __table_args__ = (
        UniqueConstraint(
            "calendar_id", "mini_service_id", name="idx_uq_calendar_mini_service"
        ),
    )

    calendar_id: Mapped[str] = mapped_column(ForeignKey("calendar.id"))
    mini_service_id: Mapped[UUID] = mapped_column(ForeignKey("mini_service.id"))
