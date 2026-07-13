"""Package for application schemas."""

from .calendar import CalendarCreate, CalendarDetail, CalendarLite, CalendarUpdate, Rules
from .event import (
    EventCreate,
    EventDetail,
    EventLite,
    EventUpdate,
    EventUpdateTime,
)
from .mini_service import (
    MiniServiceCreate,
    MiniServiceDetail,
    MiniServiceLite,
    MiniServiceUpdate,
)
from .reservation_service import (
    ReservationServiceCreate,
    ReservationServiceDetail,
    ReservationServiceLite,
    ReservationServiceUpdate,
)
from .user import UserCreate, UserDetail, UserLite, UserUpdate

__all__ = [
    "CalendarCreate",
    "CalendarDetail",
    "CalendarLite",
    "CalendarUpdate",
    "EventCreate",
    "EventDetail",
    "EventLite",
    "EventUpdate",
    "EventUpdateTime",
    "MiniServiceCreate",
    "MiniServiceDetail",
    "MiniServiceLite",
    "MiniServiceUpdate",
    "ReservationServiceCreate",
    "ReservationServiceDetail",
    "ReservationServiceLite",
    "ReservationServiceUpdate",
    "Rules",
    "UserCreate",
    "UserDetail",
    "UserLite",
    "UserUpdate",
]
