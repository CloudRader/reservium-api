"""
User ORM model and its dependencies.
"""
from uuid import uuid4
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from db.base_class import Base


class User(Base):
    """
    User model to create and manipulate user entity in the database.
    """
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String, unique=True, nullable=False)
    user_token = Column(String, unique=True, nullable=False)
