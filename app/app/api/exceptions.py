"""Package for App Exceptions."""

from enum import Enum
from typing import Any
from uuid import UUID

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


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


# pylint: disable=unused-argument
# reason: Exception handlers require request and exception parameter.
def get_exception_response_detail(status_code: int, desc: str) -> dict:
    """
    Get exception response detail for openAPI documentation.

    :param status_code: Status code of the exception.
    :param desc: Description of the exception.

    :return dict: Exception response detail.
    """
    return {status_code: {"model": Message, "description": desc}}


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

    def to_response(self) -> JSONResponse:
        """Convert exception to a JSONResponse."""
        return JSONResponse(
            status_code=self.status_code,
            content={"message": self.message, **self.details},
        )

    @classmethod
    def response(cls) -> dict:
        """Return OpenAPI response documentation for this exception."""
        return get_exception_response_detail(cls.STATUS_CODE, cls.DESCRIPTION)


def app_exception_handler(request: Request, exc: BaseAppError) -> JSONResponse:
    """Handle BaseAppError exceptions."""
    return exc.to_response()


class EntityNotFoundError(BaseAppError):
    """Exception for when entity is not found in database."""

    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DESCRIPTION = "Entity not found."

    def __init__(
        self,
        entity: Entity,
        entity_id: UUID | str | int,
        message: str | None = None,
        **kwargs: Any,
    ):
        final_message = message or f"Entity {entity.value} with id {entity_id} was not found."
        super().__init__(
            message=final_message,
            status_code=self.STATUS_CODE,
            entity=entity.value,
            entity_id=entity_id,
            **kwargs,
        )


class PermissionDeniedError(BaseAppError):
    """Exception raised when a user does not have the required permissions."""

    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DESCRIPTION = "User does not have the required permissions."

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


ERROR_RESPONSES = {
    "400": {
        **BaseAppError.response(),
    },
    "403": {
        **PermissionDeniedError.response(),
    },
    "404": {
        **EntityNotFoundError.response(),
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
