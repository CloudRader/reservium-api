"""Shortcuts to easily import schemes."""

from .access_card_system import (
    ClubAccessSystemRequest,
    VarSymbolCreateUpdate,
    VarSymbolDelete,
)
from .calendar import CalendarCreate, CalendarDetail, CalendarLite, CalendarUpdate, Rules
from .email import EmailCreate, EmailMeta, RegistrationFormCreate
from .event import (
    EventCreate,
    EventDetail,
    EventLite,
    EventUpdate,
    EventUpdateTime,
)
from .keycloak import UserKeycloak
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
    "ClubAccessSystemRequest",
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
    "UserKeycloak",
    "UserLite",
    "UserUpdate",
    "VarSymbolCreateUpdate",
    "VarSymbolDelete",
]
