"""Package for API modules."""

from .docs import fastapi_docs
from .exceptions import (
    ERROR_RESPONSES,
    BaseAppError,
    Entity,
    EntityNotFoundError,
    ExternalAPIError,
    Message,
    MethodNotAllowedError,
    NotImplementedFunctionError,
    PermissionDeniedError,
    SoftValidationError,
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
    "SoftValidationError",
    "ExternalAPIError",
    # User authenticator
    "get_oauth_session",
    "get_request",
    "authenticate_user",
    "get_current_user",
    "get_current_token",
    # Docs
    "fastapi_docs",
]
