"""
Shortcuts to easily import schemes.
"""
from .user import User, UserCreate, UserUpdate, UserInDB
from .event import EventCreate, RegistrationFormCreate
from .data_is import UserIS, RoleList, Role, ServiceList, ServiceValidity, \
    InformationFromIS, LimitObject, Service, Zone, Room
from .calendar import Calendar, CalendarCreate, CalendarUpdate, CalendarInDBBase, Rules
from .mini_service import MiniService, MiniServiceCreate, MiniServiceUpdate, MiniServiceInDBBase
from .reservation_service import ReservationService, ReservationServiceCreate, \
    ReservationServiceUpdate, ReservationServiceInDBBase
from .email import EmailCreate

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Calendar", "CalendarCreate", "CalendarUpdate", "CalendarInDBBase", "Rules",
    "MiniService", "MiniServiceCreate", "MiniServiceUpdate", "MiniServiceInDBBase",
    "ReservationService", "ReservationServiceCreate", "ReservationServiceUpdate",
    "ReservationServiceInDBBase",
    "EventCreate", "EmailCreate", "RegistrationFormCreate",
    "UserIS", "RoleList", "Role", "ServiceList", "ServiceValidity", "InformationFromIS",
    "Zone", "Room", "LimitObject", "Service"
]
