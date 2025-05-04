"""
Calendar ORM model and its dependencies.
"""
from typing import Type, Any, TYPE_CHECKING
import json
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy.types import TypeDecorator, TEXT
from db.base_class import Base
from schemas.calendar import Rules
from models.soft_delete_mixin import SoftDeleteMixin


if TYPE_CHECKING:
    from models.reservation_service import ReservationService
    from models.event import Event

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
        return json.dumps(value.model_dump())

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Rules.model_validate_json(value)

    def process_literal_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, dict):
            value = Rules(**value)
        return json.dumps(value.model_dump())

    def copy(self, **kw):
        return RulesType(self.impl)


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
# pylint: disable=unsubscriptable-object
# reason: Custom SQLAlchemy type, based on TypeDecorator.
class Calendar(Base, SoftDeleteMixin):
    """
    Calendar model to create and manipulate user entity in the database.
    """

    id: Mapped[str] = mapped_column(primary_key=True)
    reservation_type: Mapped[str] = mapped_column(unique=True, nullable=False)
    color: Mapped[str] = mapped_column(default="#05baf5", nullable=False)
    max_people: Mapped[int] = mapped_column(default=0, nullable=False)
    more_than_max_people_with_permission: Mapped[bool] = mapped_column(nullable=False, default=True)
    collision_with_itself: Mapped[bool] = mapped_column(default=False, nullable=False)
    collision_with_calendar: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    club_member_rules: Mapped[Rules] = mapped_column(RulesType(), nullable=True)
    active_member_rules: Mapped[Rules] = mapped_column(RulesType(), nullable=False)
    manager_rules: Mapped[Rules] = mapped_column(RulesType(), nullable=False)

    reservation_service_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),
                                                         ForeignKey("reservation_service.id"))

    reservation_service: Mapped["ReservationService"] = relationship(
        back_populates="calendars")
    events: Mapped[list["Event"]] = relationship(
        back_populates="calendar", lazy="selectin")
    mini_services: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

# pylint: enable=too-few-public-methods
