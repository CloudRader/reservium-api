"""
Package for API modules.
"""

from .utils import EntityNotFoundException, NotImplementedException, \
    MethodNotAllowedException, Entity, Message, method_not_allowed_exception_handler, \
    entity_not_found_exception_handler, not_implemented_exception_handler, \
    fastapi_docs
from .google_auth import auth_google
from .user_authenticator import get_oauth_session, get_request, \
    authenticate_user, get_current_user
__all_ = [
    "EntityNotFoundException", "NotImplementedException", "MethodNotAllowedException",
    "Entity", "Message", "method_not_allowed_exception_handler",
    "entity_not_found_exception_handler", "not_implemented_exception_handler", "fastapi_docs",
    "auth_google",
    "get_oauth_session", "get_request", "authenticate_user", "get_current_user"
]
