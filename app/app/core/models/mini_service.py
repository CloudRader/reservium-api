"""
Mini service ORM model and its dependencies.
"""

from typing import TYPE_CHECKING

from core.models.base_class import Base
from core.models.soft_delete_mixin import SoftDeleteMixin
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from core.models.calendar import Calendar
    from core.models.reservation_service import ReservationService


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
# pylint: disable=unsubscriptable-object
# reason: Custom SQLAlchemy type, based on TypeDecorator.
class MiniService(Base, SoftDeleteMixin):
    """
    Mini service model to create and manipulate mini service entity in the database.
    """

    __tablename__ = "mini_service"

    name: Mapped[str] = mapped_column(nullable=False)
    access_group: Mapped[str] = mapped_column(nullable=True)
    room_id: Mapped[int] = mapped_column(nullable=True)
    reservation_service_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reservation_service.id")
    )

    reservation_service: Mapped["ReservationService"] = relationship(
        back_populates="mini_services"
    )
    calendars: Mapped[list["Calendar"]] = relationship(
        secondary="calendar_mini_service_association",
        back_populates="mini_services",
        lazy="selectin",
    )
    lockers_id: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=False, default=list
    )


# pylint: enable=too-few-public-methods
