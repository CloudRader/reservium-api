"""
Package for API modules.
"""

from .utils import get_request, exchange_code_for_token, CLIENT_ID, \
    CLIENT_SECRET, REDIRECT_URI, EntityNotFoundException, NotImplementedException, \
    MethodNotAllowedException, Entity, Message, method_not_allowed_exception_handler, \
    entity_not_found_exception_handler, not_implemented_exception_handler, \
    fastapi_docs
from .google_auth import auth_google

__all_ = [
    "get_request", "exchange_code_for_token", "CLIENT_ID", "CLIENT_SECRET", "REDIRECT_URI",
    "EntityNotFoundException", "NotImplementedException", "MethodNotAllowedException",
    "Entity", "Message", "method_not_allowed_exception_handler",
    "entity_not_found_exception_handler", "not_implemented_exception_handler", "fastapi_docs",
    "auth_google",
    "get_current_user"
]
