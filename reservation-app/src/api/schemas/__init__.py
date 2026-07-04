"""Shortcuts to easily import schemes."""

from .access_card_system import (
    ClubAccessSystemRequest,
)
from .calendar import CalendarCreate, CalendarDetail, CalendarLite, CalendarUpdate, Rules
from .current_user import CurrentUser
from .email import EmailCreate, EmailMeta, RegistrationFormCreate
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
from .well_known import WellKnownResponse

__all__ = [
    "CalendarCreate",
    "CalendarDetail",
    "CalendarLite",
    "CalendarUpdate",
    "ClubAccessSystemRequest",
    "CurrentUser",
    "EmailCreate",
    "EmailMeta",
    "EventCreate",
    "EventDetail",
    "EventLite",
    "EventUpdate",
    "EventUpdateTime",
    "MiniServiceCreate",
    "MiniServiceDetail",
    "MiniServiceLite",
    "MiniServiceUpdate",
    "RegistrationFormCreate",
    "ReservationServiceCreate",
    "ReservationServiceDetail",
    "ReservationServiceLite",
    "ReservationServiceUpdate",
    "Rules",
    "UserCreate",
    "UserDetail",
    "UserLite",
    "UserUpdate",
    "WellKnownResponse",
]
