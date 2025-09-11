"""Package for App Exceptions."""

import re
from enum import Enum
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError


class Message(BaseModel):
    """Model for response message."""

    message: str


class Entity(Enum):
    """Enum for entity names."""

    USER = "User"
    CALENDAR = "Calendar"
    EVENT = "Event"
    MINI_SERVICE = "Mini Service"
    RESERVATION_SERVICE = "Reservation Service"
    EMAIL = "Email"


def get_exception_response_detail(status_code: int, desc: str) -> dict:
    """
    Get exception response detail for openAPI documentation.

    :param status_code: Status code of the exception.
    :param desc: Description of the exception.

    :return dict: Exception response detail.
    """
    return {status_code: {"model": Message, "description": desc}}


def parse_integrity_error(exc: IntegrityError) -> tuple[int, dict[str, Any]]:
    """Parse DB integrity error and map to HTTP response."""
    orig = getattr(exc, "orig", None)
    text = str(orig or exc)

    constraint = getattr(orig, "constraint_name", None)
    detail = getattr(orig, "detail", None)

    constraint_map = {
        "uq_": (status.HTTP_409_CONFLICT, "Duplicate value for unique field(s)."),
        "pk_": (status.HTTP_409_CONFLICT, "Duplicate primary key."),
        "fk_": (status.HTTP_400_BAD_REQUEST, "Invalid reference: related record not found."),
        "ck_": (status.HTTP_400_BAD_REQUEST, "Invalid value: violates check constraint."),
    }

    if constraint:
        for prefix, (code, message) in constraint_map.items():
            if constraint.startswith(prefix):
                return code, {"message": message, "constraint": constraint}

    match = re.search(r"DETAIL:\s+Key\s+\((.*?)\)=\((.*?)\)\s+already exists", text)
    if match:
        fields, values = match.groups()
        return status.HTTP_409_CONFLICT, {
            "message": f"Duplicate value for field(s): {fields}",
            "fields": fields,
            "values": values,
        }

    return status.HTTP_400_BAD_REQUEST, {"message": detail or text or "Database integrity error."}


class BaseAppError(Exception):
    """Base exception class for custom exceptions."""

    STATUS_CODE: int = status.HTTP_400_BAD_REQUEST
    DESCRIPTION: str = "An error occurred."

    def __init__(
        self,
        message: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ):
        self.message = message or self.DESCRIPTION
        self.status_code = status_code or self.STATUS_CODE
        self.details = kwargs  # Extra context if needed

    def to_response(self) -> ORJSONResponse:
        """Convert exception to a ORJSONResponse."""
        return ORJSONResponse(
            status_code=self.status_code,
            content={"message": self.message, **self.details},
        )

    @classmethod
    def response(cls) -> dict:
        """Return OpenAPI response documentation for this exception."""
        return get_exception_response_detail(cls.STATUS_CODE, cls.DESCRIPTION)


class SoftValidationError(BaseAppError):
    """Custom soft error that returns a 200 OK with a message."""

    STATUS_CODE = status.HTTP_200_OK
    DESCRIPTION = "Soft validation error that doesn't interrupt flow."

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message or self.DESCRIPTION,
            status_code=self.STATUS_CODE,
            **kwargs,
        )


class EntityNotFoundError(BaseAppError):
    """Exception for when entity is not found in database."""

    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DESCRIPTION = "Entity not found."

    def __init__(
        self,
        entity: Entity,
        entity_id: str | int,
        message: str | None = None,
        **kwargs: Any,
    ):
        entity_id_str = str(entity_id)
        final_message = message or f"Entity {entity.value} with id {entity_id} was not found."
        super().__init__(
            message=final_message,
            status_code=self.STATUS_CODE,
            entity=entity.value,
            entity_id=entity_id_str,
            **kwargs,
        )


class PermissionDeniedError(BaseAppError):
    """Exception raised when a user does not have the required permissions."""

    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DESCRIPTION = "UserLite does not have the required permissions."

    def __init__(self, message: str | None = None, **kwargs):
        super().__init__(
            message=message or self.DESCRIPTION,
            status_code=self.STATUS_CODE,
            **kwargs,
        )


class UnauthorizedError(BaseAppError):
    """Exception raised when a user does not have the required permissions."""

    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DESCRIPTION = "There's some kind of authorization problem."

    def __init__(self, message: str | None = None, **kwargs):
        super().__init__(
            message=message or self.DESCRIPTION,
            status_code=self.STATUS_CODE,
            **kwargs,
        )


class MethodNotAllowedError(BaseAppError):
    """Exception for not allowed methods."""

    STATUS_CODE = status.HTTP_405_METHOD_NOT_ALLOWED
    DESCRIPTION = "Method not allowed."

    def __init__(self, entity: Entity, request: Request):
        message = f"Method {request.method} is not allowed for entity {entity.value}"
        super().__init__(message=message, entity=entity.value)


class NotImplementedFunctionError(BaseAppError):
    """Exception for when a functionality is not yet implemented."""

    STATUS_CODE = status.HTTP_501_NOT_IMPLEMENTED
    DESCRIPTION = "Method not implemented."

    def __init__(self):
        message = self.DESCRIPTION
        super().__init__(message=message)


class ExternalAPIError(BaseAppError):
    """Exception for failures from external api."""

    STATUS_CODE = status.HTTP_502_BAD_GATEWAY
    DESCRIPTION = "External api call failed."

    def __init__(self, message: str | None = None, **kwargs):
        super().__init__(
            message=message or self.DESCRIPTION,
            status_code=self.STATUS_CODE,
            **kwargs,
        )


class DatabaseIntegrityError(BaseAppError):
    """Wrap SQLAlchemy IntegrityError for FastAPI style exceptions."""

    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DESCRIPTION = "Database integrity error."

    def __init__(self, exc: IntegrityError):
        code, content = parse_integrity_error(exc)
        super().__init__(
            message=content.get("message", self.DESCRIPTION),
            status_code=code,
            **{k: v for k, v in content.items() if k != "message"},
        )


def register_errors_handlers(app: FastAPI) -> None:
    """Register global error handlers."""

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError):  # noqa: ARG001
        """Wrap IntegrityError into DatabaseIntegrityError."""
        raise DatabaseIntegrityError(exc)

    @app.exception_handler(BaseAppError)
    def app_exception_handler(request: Request, exc: BaseAppError) -> ORJSONResponse:  # noqa: ARG001
        """Handle BaseAppError exceptions."""
        return exc.to_response()


ERROR_RESPONSES = {
    "400": {
        **BaseAppError.response(),
    },
    "401": {
        **UnauthorizedError.response(),
    },
    "403": {
        **PermissionDeniedError.response(),
    },
    "404": {
        **EntityNotFoundError.response(),
    },
    "400_404": {
        **BaseAppError.response(),
        **EntityNotFoundError.response(),
    },
    "401_403": {
        **UnauthorizedError.response(),
        **PermissionDeniedError.response(),
    },
    "400_401_403": {
        **BaseAppError.response(),
        **UnauthorizedError.response(),
        **PermissionDeniedError.response(),
    },
    "400_401_403_404": {
        **BaseAppError.response(),
        **UnauthorizedError.response(),
        **PermissionDeniedError.response(),
        **EntityNotFoundError.response(),
    },
}
