"""
User ORM model and its dependencies.
"""
from typing import Optional, List
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from db.base_class import Base
from models.soft_delete_mixin import SoftDeleteMixin


# pylint: disable=too-few-public-methods
# reason: ORM model does not require to have any public methods
class User(Base, SoftDeleteMixin):
    """
    User model to create and manipulate user entity in the database.
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    active_member = Column(Boolean, unique=False, nullable=False, default=False)
    section_head = Column(Boolean, unique=False, nullable=False, default=False)
    roles: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), unique=False, nullable=True)

# pylint: enable=too-few-public-methods
