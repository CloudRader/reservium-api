"""
Package for CRUD repositories for each domain type, used to handle
operations over database.
"""

from .crud_base import CRUDBase
from .crud_calendar import CRUDCalendar
from .crud_event import CRUDEvent
from .crud_mini_service import CRUDMiniService
from .crud_reservation_service import CRUDReservationService
from .crud_user import CRUDUser

__all__ = [
    "CRUDBase",
    "CRUDCalendar",
    "CRUDUser",
    "CRUDMiniService",
    "CRUDReservationService",
    "CRUDEvent",
]
