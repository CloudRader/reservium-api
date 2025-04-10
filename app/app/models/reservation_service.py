"""
Reservation service ORM model and its dependencies.
"""
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.base_class import Base
from models.soft_delete_mixin import SoftDeleteMixin
# from models import CalendarModel, MiniServiceModel


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
class ReservationService(Base, SoftDeleteMixin):
    """
    Reservation service model to create and manipulate reservation service entity in the database.
    """
    __tablename__ = "reservation_service"

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    alias: Mapped[str] = mapped_column(unique=True, nullable=False)
    public: Mapped[bool] = mapped_column(nullable=False, default=True)
    web: Mapped[str] = mapped_column(nullable=True)
    contact_mail: Mapped[str] = mapped_column(nullable=True)

    calendars: Mapped["Calendar"] = relationship("Calendar",
                                                    back_populates="reservation_service")
    mini_services: Mapped["MiniService"] = relationship("MiniService",
                                                           back_populates="reservation_service")

# pylint: enable=too-few-public-methods
