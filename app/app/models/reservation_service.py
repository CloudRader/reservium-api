"""
Reservation service ORM model and its dependencies.
"""
from uuid import uuid4
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base_class import Base


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
class ReservationService(Base):
    """
    Reservation service model to create and manipulate reservation service entity in the database.
    """
    __tablename__ = "reservation_service"
    is_active = Column(Boolean, nullable=False, default=True)

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, unique=True, nullable=False)
    alias = Column(String, unique=True, nullable=False)
    web = Column(String, nullable=True)
    contact_mail = Column(String, nullable=True)

    calendars = relationship("Calendar", back_populates="reservation_service")
    mini_services = relationship("MiniService", back_populates="reservation_service")

# pylint: enable=too-few-public-methods
