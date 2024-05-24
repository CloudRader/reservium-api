"""
Mini service ORM model and its dependencies.
"""
from uuid import uuid4
from typing import Optional, List
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base_class import Base


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
class MiniService(Base):
    """
    Mini service model to create and manipulate mini service entity in the database.
    """
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, unique=True, nullable=False)
    service_alias: Mapped[Optional[List[str]]] = mapped_column(String, nullable=False)

# pylint: enable=too-few-public-methods
