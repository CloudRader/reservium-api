"""Package for API modules."""

from .docs import fastapi_docs
from .exceptions import (
    ERROR_RESPONSES,
    BaseAppError,
    Entity,
    EntityNotFoundError,
    Message,
    MethodNotAllowedError,
    NotImplementedFunctionError,
    PermissionDeniedError,
    UnauthorizedError,
    app_exception_handler,
)
from .user_authenticator import (
    authenticate_user,
    get_current_token,
    get_current_user,
    get_oauth_session,
    get_request,
)
from .utils import (
    check_night_reservation,
    control_available_reservation_time,
    control_collision,
    modify_url_scheme,
)

__all__ = [
    # Exceptions
    "EntityNotFoundError",
    "NotImplementedFunctionError",
    "MethodNotAllowedError",
    "BaseAppError",
    "Entity",
    "Message",
    "app_exception_handler",
    "PermissionDeniedError",
    "UnauthorizedError",
    "ERROR_RESPONSES",
    # Utils
    "control_collision",
    "check_night_reservation",
    "control_available_reservation_time",
    "modify_url_scheme",
    # User authenticator
    "get_oauth_session",
    "get_request",
    "authenticate_user",
    "get_current_user",
    "get_current_token",
    # Docs
    "fastapi_docs",
]
