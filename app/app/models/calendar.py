"""
Calendar ORM model and its dependencies.
"""
from uuid import uuid4
from sqlalchemy import Column, String, JSON, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from db.base_class import Base


class Calendar(Base):
    """
    Calendar model to create and manipulate user entity in the database.
    """
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    calendar_id = Column(String, unique=True, nullable=False)
    service_name = Column(String, unique=False, nullable=False)
    reservation_type = Column(String, unique=True, nullable=False)
    event_name = Column(String, nullable=False)
    max_people = Column(Integer, default=0)
    collision_with_calendar = Column(ARRAY(String), nullable=False)
    club_member_rules = Column(JSON, nullable=True)
    active_member_rules = Column(JSON, nullable=False)
    manager_rules = Column(JSON, nullable=False)
