"""
Utils for API.
"""
from typing import Annotated
from enum import Enum
from uuid import UUID
from fastapi import Depends, status, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from schemas import UserIS, RoleList
from services import UserService

import httpx

# For testing on my computer.
# CLIENT_ID = "7b6b8b84740117ff55c72c8c74f9fd4c75a82b1e471b411e6f6a9ca5c063af18"
# CLIENT_SECRET = "903e0b4d8d5cfb69ba540b782e339979b829652ed4d97fb5075f6f6ff73ad284"
# REDIRECT_URI = "https://10.0.52.106:8000/auth_is/login/callback"


# For buk server.
CLIENT_ID = "e36219f8fdd7619dfa80754aa17c47e38c04e4407d37c26e48058531c82b18c1"
CLIENT_SECRET = "44218c6184e21ee1e679586bcbe8d5b1727d6a771c6619a46aa821fe1eff4e98"
REDIRECT_URI = "https://rezervace.buk.cvut.cz:8000/auth_is/login/callback"


async def get_request(token: str, request: str):
    """
    Make an authenticated GET request to the IS.

    :param token: The authorization token.
    :param request: The API endpoint to request data.

    :return: The JSON response from the API.
    """
    info_endpoint = "https://api.is.buk.cvut.cz/v1/" + request

    async with httpx.AsyncClient() as client:
        response = await client.get(info_endpoint, headers={"Authorization": f"Bearer {token}"})

        if response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="There's some kind of authorization problem",
                headers={"WWW-Authenticate": "Bearer"},
            )

        response.raise_for_status()

        response_data = response.json()

    return response_data


async def exchange_code_for_token(user_service: Annotated[UserService, Depends(UserService)],
                                  code: str):
    """
    Exchange an authorization code for an access token and create a user.

    :param user_service: User service.
    :param code: The authorization code to exchange for an access token.

    :return: The created user with the retrieved roles and token.
    """
    token_endpoint = "https://is.buk.cvut.cz/oauth/token"
    client_credentials = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_endpoint, data=client_credentials)
        if response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="There's some kind of authorization problem",
                headers={"WWW-Authenticate": "Bearer"},
            )
        response_data = response.json()

        token = response_data.get("access_token", "")
        response_user = await client.get("https://api.is.buk.cvut.cz/v1/users/me",
                                         headers={"Authorization": f"Bearer {token}"})
        response_data_user = response_user.json()

    user_data = UserIS(**response_data_user)
    roles = RoleList(roles=await get_request(token, "/user_roles/mine")).roles
    return user_service.create_user(user_data, roles, token)


class Message(BaseModel):
    """Model for response message."""
    message: str


class Entity(Enum):
    """Enum for entity names."""
    USER = "User"
    CALENDAR = "Calendar"
    EVENT = "Event"
    MINI_SERVICE = "Mini Service"


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


class MethodNotAllowedException(Exception):
    """Exception for not allowed methods."""
    STATUS_CODE = status.HTTP_405_METHOD_NOT_ALLOWED
    DESCRIPTION = "Method not allowed."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(self, entity: Entity):
        self.entity = entity


def method_not_allowed_exception_handler(
        request: Request, exc: MethodNotAllowedException
) -> JSONResponse:
    """Exception handler for MethodNotAllowedException.

    :param request: Request that caused the exception.
    :param exc: The exception.
    """
    return JSONResponse(
        status_code=exc.STATUS_CODE,
        content={
            "message": f"Method {request.method} is not allowed for entity {exc.entity.value}"
        },
    )


class EntityNotFoundException(Exception):
    """
    Exception for when entity is not found in database.
    """
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DESCRIPTION = "Entity not found."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(self, entity: Entity, entity_id: UUID | str):
        self.entity = entity
        self.entity_uuid = entity_id


def entity_not_found_exception_handler(
        request: Request, exc: EntityNotFoundException
) -> JSONResponse:
    """Exception handler for EntityNotFoundException.

    :param request: Request that caused the exception.
    :param exc: The exception.
    """
    return JSONResponse(
        status_code=exc.STATUS_CODE,
        content={
            "message": f"Entity {exc.entity.value} with id {exc.entity_uuid} "
                       f"was not found or you don't "
                       f"have permission to do operation with that entity."
        },
    )


class NotImplementedException(Exception):
    """Exception for when a functionality is not yet implemented."""
    STATUS_CODE = status.HTTP_501_NOT_IMPLEMENTED
    DESCRIPTION = "Method not implemented."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)


def not_implemented_exception_handler(
        request: Request, exc: NotImplementedException
) -> JSONResponse:
    """Exception handler for NotImplementedException.

    :param request: Request that caused the exception.
    :param exc: The exception.
    """
    return JSONResponse(
        status_code=exc.STATUS_CODE,
        content={
            "message": exc.DESCRIPTION
        },
    )


# pylint: disable=too-few-public-methods
# reason: no more public methods needed.
class FastApiDocs:
    """Information for fastapi documentation."""
    NAME = "Reservation System of the Buben Club"
    DESCRIPTION = \
        "Reservation System of the Buben Club API is " \
        "a REST API that offers you an access to our " \
        "application!"
    VERSION = "1.0.0"
    AUTHORISATION_TAG = {
        "name": "users",
        "description": "Authorisation in IS.",
    }
    CALENDAR_TAG = {
        "name": "calendars",
        "description": "Operations with calendars.",
    }
    MINI_SERVICE_TAG = {
        "name": "mini services",
        "description": "Operations with mini services.",
    }
    EVENT_TAG = {
        "name": "events",
        "description": "Operations with events.",
    }

    def get_tags_metadata(self):
        """Get tags metadata."""
        return [
            self.AUTHORISATION_TAG,
            self.CALENDAR_TAG,
            self.MINI_SERVICE_TAG,
            self.EVENT_TAG,
        ]


fastapi_docs = FastApiDocs()

# pylint: enable=too-few-public-methods
