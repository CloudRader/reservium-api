"""
SQLAlchemy Easy Soft-Delete
"""
from sqlalchemy_easy_softdelete.mixin import generate_soft_delete_mixin_class
from datetime import datetime


class SoftDeleteMixin(generate_soft_delete_mixin_class()):
    """
    Easily add soft-deletion to your SQLAlchemy Models and
    automatically filter out soft-deleted objects from your
    queries and relationships.
    """
    deleted_at: datetime
