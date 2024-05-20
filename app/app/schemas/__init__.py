"""
Shortcuts to easily import schemes.
"""
from .user import User, UserCreate, UserUpdate, UserInDB
from .event import EventInput
from .user_is import UserIS
from .zone import Zone, Room
from .calendar import Calendar, CalendarCreate, CalendarUpdate, CalendarInDBBase, Rules
from .mini_service import MiniService, MiniServiceCreate, MiniServiceUpdate, MiniServiceInDBBase

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "Calendar", "CalendarCreate", "CalendarUpdate", "CalendarInDBBase", "Rules",
    "MiniService", "MiniServiceCreate", "MiniServiceUpdate", "MiniServiceInDBBase",
    "EventInput",
    "UserIS",
    "Zone", "Room"
]