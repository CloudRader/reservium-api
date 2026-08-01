"""Package for application schemas."""

from .calendar import CalendarCreate, CalendarSchema, CalendarUpdate, Rules
from .event import (
    EventCreate,
    EventDetail,
    EventLite,
    EventUpdate,
    EventUpdateTime,
)
from .mini_service import (
    MiniServiceCreate,
    MiniServiceSchema,
    MiniServiceUpdate,
)
from .reservation_service import (
    ReservationServiceCreate,
    ReservationServiceDetail,
    ReservationServiceLite,
    ReservationServiceUpdate,
)
from .user import UserCreate, UserSchema, UserUpdate

__all__ = [
    "CalendarCreate",
    "CalendarSchema",
    "CalendarUpdate",
    "EventCreate",
    "EventDetail",
    "EventLite",
    "EventUpdate",
    "EventUpdateTime",
    "MiniServiceCreate",
    "MiniServiceSchema",
    "MiniServiceUpdate",
    "ReservationServiceCreate",
    "ReservationServiceDetail",
    "ReservationServiceLite",
    "ReservationServiceUpdate",
    "Rules",
    "UserCreate",
    "UserSchema",
    "UserUpdate",
]
