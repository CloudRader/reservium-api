"""
Calendar ORM model and its dependencies.
"""
from typing import List, Optional
from sqlalchemy import Column, String, JSON, Integer, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from db.base_class import Base


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
class Calendar(Base):
    """
    Calendar model to create and manipulate user entity in the database.
    """
    calendar_id = Column(String, primary_key=True, unique=True, nullable=False)
    service_alias = Column(String, unique=False, nullable=False)
    reservation_type = Column(String, unique=True, nullable=False)
    event_name = Column(String, nullable=False)
    max_people = Column(Integer, default=0)
    collision_with_itself = Column(Boolean, nullable=False)
    collision_with_calendar: Mapped[Optional[List[str]]] = \
        mapped_column(ARRAY(String), nullable=True)
    club_member_rules = Column(JSON, nullable=True)
    active_member_rules = Column(JSON, nullable=False)
    manager_rules = Column(JSON, nullable=False)

    mini_services: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

# pylint: enable=too-few-public-methods
