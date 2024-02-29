"""
Package for CRUD repositories for each domain type, used to handle
operations over database.
"""
from .crud_base import AbstractCRUDBase, CRUDBase

__all__ = ["AbstractCRUDBase", "CRUDBase"]
