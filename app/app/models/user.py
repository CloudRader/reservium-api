"""
User ORM model and its dependencies.
"""
from uuid import uuid4
from typing import Optional, List
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from db.base_class import Base


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
class User(Base):
    """
    User model to create and manipulate user entity in the database.
    """
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String, unique=True, nullable=False)
    user_token = Column(String, unique=True, nullable=False)
    active_member = Column(Boolean, unique=False, nullable=False)
    roles: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), unique=False, nullable=True)

# pylint: enable=too-few-public-methods
