"""
User ORM model and its dependencies.
"""
from typing import Optional, List
from sqlalchemy import String
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

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    active_member: Mapped[bool] = mapped_column(unique=False, nullable=False, default=False)
    section_head: Mapped[bool] = mapped_column(unique=False, nullable=False, default=False)
    roles: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), unique=False, nullable=True)

# pylint: enable=too-few-public-methods
