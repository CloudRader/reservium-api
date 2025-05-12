"""
Shortcuts to easily import schemes.
"""
from .user import User, UserCreate, UserUpdate, UserInDB
from .event import EventCreate, EventCreateToDb, EventUpdate, Event, EventInDB, EventUpdateTime, \
    EventWithExtraDetails
from .data_is import UserIS, RoleList, Role, ServiceList, ServiceValidity, \
    InformationFromIS, LimitObject, Service, Zone, Room
from .calendar import Calendar, CalendarCreate, CalendarUpdate, CalendarInDBBase, Rules
from .mini_service import MiniService, MiniServiceCreate, MiniServiceUpdate, MiniServiceInDBBase
from .reservation_service import ReservationService, ReservationServiceCreate, \
    ReservationServiceUpdate, ReservationServiceInDBBase
from .email import EmailCreate, RegistrationFormCreate, EmailMeta
from .access_card_system import VarSymbolCreateUpdate, VarSymbolDelete, ClubAccessSystemRequest

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Calendar", "CalendarCreate", "CalendarUpdate", "CalendarInDBBase", "Rules",
    "MiniService", "MiniServiceCreate", "MiniServiceUpdate", "MiniServiceInDBBase",
    "ReservationService", "ReservationServiceCreate", "ReservationServiceUpdate",
    "ReservationServiceInDBBase",
    "EventCreate", "EventCreateToDb", "EventUpdate", "Event", "EventInDB", "EventUpdateTime",
    "EventWithExtraDetails",
    "EmailCreate", "RegistrationFormCreate",
    "UserIS", "RoleList", "Role", "ServiceList", "ServiceValidity", "InformationFromIS",
    "Zone", "Room", "LimitObject", "Service", "EmailMeta",
    "VarSymbolCreateUpdate", "VarSymbolDelete", "ClubAccessSystemRequest",
]
