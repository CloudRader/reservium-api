"""
Mini service ORM model and its dependencies.
"""
from uuid import uuid4
from sqlalchemy import Column, String
from db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID


class MiniService(Base):
    """
    Mini service model to create and manipulate mini service entity in the database.
    """
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, unique=True, nullable=False)
    service_alias = Column(String, nullable=False)

# pylint: enable=too-few-public-methods
