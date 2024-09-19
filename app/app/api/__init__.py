"""
Package for API modules.
"""

from .utils import EntityNotFoundException, NotImplementedException, control_collision, \
    MethodNotAllowedException, Entity, Message, method_not_allowed_exception_handler, \
    entity_not_found_exception_handler, not_implemented_exception_handler, \
    fastapi_docs, check_night_reservation, control_available_reservation_time, \
    modify_url_scheme
from .google_auth import auth_google
from .user_authenticator import get_oauth_session, get_request, \
    authenticate_user, get_current_user, get_current_token
from .emails import send_email

__all_ = [
    "EntityNotFoundException", "NotImplementedException", "MethodNotAllowedException",
    "Entity", "Message", "method_not_allowed_exception_handler",
    "entity_not_found_exception_handler", "not_implemented_exception_handler", "fastapi_docs",
    "check_night_reservation", "control_available_reservation_time", "control_collision"
    "auth_google", "modify_url_scheme", "send_email",
    "get_oauth_session", "get_request", "authenticate_user", "get_current_user", "get_current_token"
]
