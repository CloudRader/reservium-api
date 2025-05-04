"""
Package for App Exceptions.
"""
from typing import Any
from enum import Enum
from uuid import UUID
from fastapi import status, Request
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
    """Get exception response detail for openAPI documentation.

    :param status_code: Status code of the exception.
    :param desc: Description of the exception.

    :return dict: Exception response detail.
    """
    return {
        status_code: {
            "model": Message,
            "description": desc
        }
    }


class BaseAppException(Exception):
    """Base exception class for custom exceptions."""

    STATUS_CODE: int = status.HTTP_400_BAD_REQUEST
    DESCRIPTION: str = "An error occurred."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(
            self, message: str | None = None,
            status_code: int | None = None,
            **kwargs: Any):
        self.message = message or self.DESCRIPTION
        self.status_code = status_code or self.STATUS_CODE
        self.details = kwargs  # Extra context if needed

    def to_response(self) -> JSONResponse:
        """Convert exception to a JSONResponse."""
        return JSONResponse(
            status_code=self.status_code,
            content={"message": self.message, **self.details},
        )


def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """
    Generic handler for BaseAppException.
    """
    return exc.to_response()


class EntityNotFoundException(BaseAppException):
    """
    Exception for when entity is not found in database.
    """

    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DESCRIPTION = "Entity not found."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(self, entity: Entity, entity_id: UUID | str | int):
        message = f"Entity {entity.value} with id {entity_id} was not found."
        super().__init__(message=message, entity=entity.value, entity_id=entity_id)


class PermissionDeniedException(BaseAppException):
    """
    Exception raised when a user does not have the required permissions.
    """

    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DESCRIPTION = "User does not have the required permissions."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(self, message: str | None = None, **kwargs):
        super().__init__(
            message=message or self.DESCRIPTION,
            status_code=self.STATUS_CODE,
            **kwargs
        )


class UnauthorizedException(BaseAppException):
    """
    Exception raised when a user does not have the required permissions.
    """

    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DESCRIPTION = "There's some kind of authorization problem."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(self, message: str | None = None, **kwargs):
        super().__init__(
            message=message or self.DESCRIPTION,
            status_code=self.STATUS_CODE,
            **kwargs
        )


class MethodNotAllowedException(BaseAppException):
    """
    Exception for not allowed methods.
    """

    STATUS_CODE = status.HTTP_405_METHOD_NOT_ALLOWED
    DESCRIPTION = "Method not allowed."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(self, entity: Entity, request: Request):
        message = f"Method {request.method} is not allowed for entity {entity.value}"
        super().__init__(message=message, entity=entity.value)


class NotImplementedException(BaseAppException):
    """
    Exception for when a functionality is not yet implemented.
    """

    STATUS_CODE = status.HTTP_501_NOT_IMPLEMENTED
    DESCRIPTION = "Method not implemented."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(self):
        message = self.DESCRIPTION
        super().__init__(message=message)
