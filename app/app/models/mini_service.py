"""
Mini service ORM model and its dependencies.
"""
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.base_class import Base
from models.soft_delete_mixin import SoftDeleteMixin

if TYPE_CHECKING:
    from models.reservation_service import ReservationService


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
# pylint: disable=unsubscriptable-object
# reason: Custom SQLAlchemy type, based on TypeDecorator.
class MiniService(Base, SoftDeleteMixin):
    """
    Mini service model to create and manipulate mini service entity in the database.
    """
    __tablename__ = "mini_service"
    __table_args__ = (
        UniqueConstraint("access_group", name="uq_mini_service_access_group"),
    )

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    access_group: Mapped[str] = mapped_column(nullable=True)
    room_id: Mapped[int] = mapped_column(nullable=True)
    reservation_service_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),
                                                         ForeignKey("reservation_service.id"))

    reservation_service: Mapped["ReservationService"] = relationship(
        back_populates="mini_services")
    lockers_id: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, default=list)

# pylint: enable=too-few-public-methods
