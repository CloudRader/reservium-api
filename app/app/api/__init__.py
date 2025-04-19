"""
Package for API modules.
"""
from .exceptions import EntityNotFoundException, NotImplementedException, \
    MethodNotAllowedException, Entity, Message, app_exception_handler, \
    BaseAppException, PermissionDeniedException, UnauthorizedException
from .utils import control_collision, check_night_reservation, \
    control_available_reservation_time, modify_url_scheme
from .user_authenticator import get_oauth_session, get_request, \
    authenticate_user, get_current_user, get_current_token
from .emails import send_email
from .google_auth import auth_google
from .docs import fastapi_docs

__all_ = [
    # Exceptions
    "EntityNotFoundException", "NotImplementedException", "MethodNotAllowedException",
    "BaseAppException", "Entity", "Message", "app_exception_handler",
    "PermissionDeniedException", "UnauthorizedException",

    # Utils
    "control_collision", "check_night_reservation", "control_available_reservation_time",
    "modify_url_scheme",

    # User authenticator
    "get_oauth_session", "get_request", "authenticate_user", "get_current_user",
    "get_current_token"

    # Emails
    "send_email"

    # Google
    "auth_google",

    # Docs
    "fastapi_docs",
]
