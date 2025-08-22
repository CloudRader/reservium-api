"""Shortcuts to easily import schemes."""

from .access_card_system import (
    ClubAccessSystemRequest,
    VarSymbolCreateUpdate,
    VarSymbolDelete,
)
from .calendar import CalendarCreate, CalendarDetail, CalendarLite, CalendarUpdate, Rules
from .data_is import (
    InformationFromIS,
    LimitObject,
    Role,
    RoleList,
    Room,
    Service,
    ServiceList,
    ServiceValidity,
    UserIS,
    Zone,
)
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

__all__ = [
    "UserLite",
    "UserDetail",
    "UserCreate",
    "UserUpdate",
    "CalendarDetail",
    "CalendarCreate",
    "CalendarUpdate",
    "CalendarLite",
    "Rules",
    "MiniServiceDetail",
    "MiniServiceCreate",
    "MiniServiceUpdate",
    "MiniServiceLite",
    "ReservationServiceDetail",
    "ReservationServiceCreate",
    "ReservationServiceUpdate",
    "ReservationServiceLite",
    "EventCreate",
    "EventUpdate",
    "EventLite",
    "EventDetail",
    "EventUpdateTime",
    "EmailCreate",
    "RegistrationFormCreate",
    "UserIS",
    "RoleList",
    "Role",
    "ServiceList",
    "ServiceValidity",
    "InformationFromIS",
    "Zone",
    "Room",
    "LimitObject",
    "Service",
    "EmailMeta",
    "VarSymbolCreateUpdate",
    "VarSymbolDelete",
    "ClubAccessSystemRequest",
]
