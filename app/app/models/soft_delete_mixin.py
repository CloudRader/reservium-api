"""
SQLAlchemy Easy Soft-Delete
"""
from datetime import datetime
from sqlalchemy_easy_softdelete.mixin import generate_soft_delete_mixin_class


# pylint: disable=too-few-public-methods
# reason: Soft Delete Mixin Class does not require to have any public methods
class SoftDeleteMixin(generate_soft_delete_mixin_class()):
    """
    Easily add soft-deletion to your SQLAlchemy Models and
    automatically filter out soft-deleted objects from your
    queries and relationships.
    """
    deleted_at: datetime
