"""
Calendar ORM model and its dependencies.
"""
from typing import List, Optional, Type, Any
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator, TEXT
from db.base_class import Base
from schemas import Rules

import json


class RulesType(TypeDecorator):
    impl = TEXT

    @property
    def python_type(self) -> Type[Any]:
        return Rules

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, dict):
            value = Rules(**value)
        return json.dumps(value.dict())

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Rules.parse_raw(value)

    def process_literal_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, dict):
            value = Rules(**value)
        return json.dumps(value.dict())

    def copy(self, **kw):
        return RulesType(self.impl)


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
class Calendar(Base):
    """
    Calendar model to create and manipulate user entity in the database.
    """
    __tablename__ = "calendar"
    is_active = Column(Boolean, nullable=False, default=True)

    id = Column(String, primary_key=True, unique=True, nullable=False)
    reservation_type = Column(String, unique=True, nullable=False)
    max_people = Column(Integer, default=0)
    collision_with_itself = Column(Boolean, nullable=False)
    collision_with_calendar: Mapped[Optional[List[str]]] = \
        mapped_column(ARRAY(String), nullable=True)
    club_member_rules = Column(RulesType, nullable=True)
    active_member_rules = Column(RulesType, nullable=False)
    manager_rules = Column(RulesType, nullable=False)
    reservation_service_uuid = Column(UUID(as_uuid=True), ForeignKey("reservation_service.uuid"))

    reservation_service = relationship("ReservationService", back_populates="calendars")
    mini_services: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

# pylint: enable=too-few-public-methods
