"""
Mini service ORM model and its dependencies.
"""
from uuid import uuid4
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base_class import Base
from models.soft_delete_mixin import SoftDeleteMixin


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
class MiniService(Base, SoftDeleteMixin):
    """
    Mini service model to create and manipulate mini service entity in the database.
    """
    __tablename__ = "mini_service"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, unique=True, nullable=False)
    reservation_service_id = Column(UUID(as_uuid=True), ForeignKey("reservation_service.id"))

    reservation_service = relationship("ReservationService", back_populates="mini_services")

# pylint: enable=too-few-public-methods
