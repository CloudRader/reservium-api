"""
Package for CRUD repositories for each domain type, used to handle
operations over database.
"""
from .crud_base import CRUDBase
from .crud_user import CRUDUser
from .crud_calendar import CRUDCalendar
from .crud_mini_service import CRUDMiniService

__all__ = ["CRUDBase",
           "CRUDCalendar",
           "CRUDUser",
           "CRUDMiniService"
           ]
