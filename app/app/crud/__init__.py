"""
Package for CRUD repositories for each domain type, used to handle
operations over database.
"""
from .crud_base import AbstractCRUDBase, CRUDBase
from .crud_user import AbstractCRUDUser, CRUDUser

__all__ = ["AbstractCRUDBase", "CRUDBase",
           "AbstractCRUDUser", "CRUDUser"]
