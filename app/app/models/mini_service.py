"""
Mini service ORM model and its dependencies.
"""
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.base_class import Base
from models.soft_delete_mixin import SoftDeleteMixin

if TYPE_CHECKING:
    from models.reservation_service import ReservationService


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
class MiniService(Base, SoftDeleteMixin):
    """
    Mini service model to create and manipulate mini service entity in the database.
    """
    __tablename__ = "mini_service"

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    reservation_service_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),
                                                         ForeignKey("reservation_service.id"))

    reservation_service: Mapped["ReservationService"] = relationship(
        back_populates="mini_services")

# pylint: enable=too-few-public-methods
