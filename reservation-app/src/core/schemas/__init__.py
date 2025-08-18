"""Shortcuts to easily import schemes."""

from .access_card_system import (
    ClubAccessSystemRequest,
    VarSymbolCreateUpdate,
    VarSymbolDelete,
)
from .calendar import Calendar, CalendarCreate, CalendarInDBBase, CalendarUpdate, Rules
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
    Event,
    EventCreate,
    EventInDB,
    EventUpdate,
    EventUpdateTime,
)
from .mini_service import (
    MiniService,
    MiniServiceCreate,
    MiniServiceInDBBase,
    MiniServiceUpdate,
)
from .reservation_service import (
    ReservationService,
    ReservationServiceCreate,
    ReservationServiceInDBBase,
    ReservationServiceUpdate,
)
from .user import User, UserCreate, UserInDB, UserUpdate

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Calendar",
    "CalendarCreate",
    "CalendarUpdate",
    "CalendarInDBBase",
    "Rules",
    "MiniService",
    "MiniServiceCreate",
    "MiniServiceUpdate",
    "MiniServiceInDBBase",
    "ReservationService",
    "ReservationServiceCreate",
    "ReservationServiceUpdate",
    "ReservationServiceInDBBase",
    "EventCreate",
    "EventUpdate",
    "Event",
    "EventInDB",
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
