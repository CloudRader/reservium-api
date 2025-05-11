"""
Reservation service ORM model and its dependencies.
"""
from typing import TYPE_CHECKING
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.base_class import Base
from models.soft_delete_mixin import SoftDeleteMixin

if TYPE_CHECKING:
    from models.calendar import Calendar
    from models.mini_service import MiniService


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
        back_populates="reservation_service", lazy="selectin")
    mini_services: Mapped[list["MiniService"]] = relationship(
        back_populates="reservation_service", lazy="selectin")
    lockers_id: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, default=list)

# pylint: enable=too-few-public-methods
