"""
Calendar ORM model and its dependencies.
"""
from typing import Type, Any
import json
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.types import TypeDecorator, TEXT
from db.base_class import Base
from schemas import Rules
from models.soft_delete_mixin import SoftDeleteMixin


# pylint: disable=too-many-ancestors
class RulesType(TypeDecorator):
    """
    Custom SQLAlchemy type to handle the serialization and deserialization of
    the `Rules` Pydantic model to and from JSON.
    """
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
class Calendar(Base, SoftDeleteMixin):
    """
    Calendar model to create and manipulate user entity in the database.
    """
    __tablename__ = "calendar"

    id = Column(String, primary_key=True, unique=True, nullable=False)
    reservation_type = Column(String, unique=True, nullable=False)
    color = Column(String, default="#05baf5")
    max_people = Column(Integer, default=0)
    collision_with_itself = Column(Boolean, nullable=False)
    collision_with_calendar = mapped_column(ARRAY(String), nullable=True)
    club_member_rules = Column(RulesType, nullable=True)
    active_member_rules = Column(RulesType, nullable=False)
    manager_rules = Column(RulesType, nullable=False)
    reservation_service_id = Column(UUID(as_uuid=True), ForeignKey("reservation_service.id"))

    reservation_service = relationship("ReservationService", back_populates="calendars")
    mini_services = mapped_column(ARRAY(String), nullable=True)

# pylint: enable=too-few-public-methods
