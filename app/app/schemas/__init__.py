"""
Shortcuts to easily import schemes.
"""
from .user import User, UserCreate, UserUpdate, UserInDB
from .event import EventInput
from .user_is import UserIS
from .zone import Zone, Room

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserInDB",
    "EventInput",
    "UserIS",
    "Zone", "Room"
]