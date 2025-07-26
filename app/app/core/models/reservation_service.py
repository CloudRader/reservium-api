"""
Reservation service ORM model and its dependencies.
"""

from typing import TYPE_CHECKING

from core.models.base_class import Base
from core.models.soft_delete_mixin import SoftDeleteMixin
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from core.models.calendar import Calendar
    from core.models.mini_service import MiniService


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
# pylint: disable=unsubscriptable-object
# reason: Custom SQLAlchemy type, based on TypeDecorator.
class ReservationService(Base, SoftDeleteMixin):
    """
    Reservation service model to create and manipulate reservation service entity in the database.
    """

    __tablename__ = "reservation_service"

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    alias: Mapped[str] = mapped_column(unique=True, nullable=False)
    public: Mapped[bool] = mapped_column(nullable=False, default=True)
    web: Mapped[str] = mapped_column(nullable=True)
    contact_mail: Mapped[str] = mapped_column(nullable=False)
    access_group: Mapped[str] = mapped_column(nullable=True)
    room_id: Mapped[int] = mapped_column(nullable=True)

    calendars: Mapped[list["Calendar"]] = relationship(
        back_populates="reservation_service", lazy="selectin"
    )
    mini_services: Mapped[list["MiniService"]] = relationship(
        back_populates="reservation_service", lazy="selectin"
    )
    lockers_id: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=False, default=list
    )


# pylint: enable=too-few-public-methods
