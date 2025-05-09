"""
Module for authenticator functions.
"""
from typing import Annotated, Any

from fastapi import HTTPException, status, Depends, Request
from requests_oauthlib import OAuth2Session
from services import UserService
from schemas import UserIS, RoleList, ServiceList, Room
from core import settings

import httpx


def get_oauth_session():
    """
    Create and return an OAuth2 session using the client ID and
    redirect URI from the application settings.

    This function initializes an OAuth2 session that can be used to
    handle the OAuth2 authentication flow, including obtaining
    authorization tokens.

    :return: OAuth2Session.
    """
    return OAuth2Session(client_id=settings.CLIENT_ID,
                         redirect_uri=settings.REDIRECT_URI)


async def get_request(token: str, request: str):
    """
    Make an authenticated GET request to the IS.

    :param token: The authorization token.
    :param request: The API endpoint to request data.

    :return: The JSON response from the API.
    """
    info_endpoint = settings.IS_SCOPES + request

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


async def authenticate_user(user_service: Annotated[UserService, Depends(UserService)],
                            token: str):
    """
     Authenticate a user using their tokens from IS.

     :param user_service: User service
     :param token: Token for user identification.

     :return: The authenticated user object if successful, otherwise Exception.
     """
    user_data = UserIS.model_validate(await get_request(token, "/users/me"))
    roles = RoleList(roles=await get_request(token, "/user_roles/mine")).roles
    services = ServiceList(services=await get_request(token,
                                                      "/services/mine")).services
    room = Room.model_validate(await get_request(token, "/rooms/mine"))
    return await user_service.create_user(user_data, roles, services, room)


async def get_current_token(request: Request) -> Any:
    """
    Retrieve token of the current user.

    :param request: The API endpoint to request data.

    :return: Token of the user.
   """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = request.session["oauth_token"]["access_token"]
        return token
    except (KeyError, TypeError) as exc:
        raise credentials_exception from exc


async def get_current_user(
        user_service: Annotated[UserService, Depends(UserService)],
        request: Request
) -> Any:
    """
    Retrieve the current user based on a JWT token.

    :param user_service: User service.
    :param request: The API endpoint to request data.

    :return: User object.
   """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = request.session.get('user_username')
    if not username:
        raise credentials_exception
    user = await user_service.get_by_username(username)
    if not user:
        raise credentials_exception
    token = request.session['oauth_token']['access_token']
    user_is = UserIS.model_validate(await get_request(token, "/users/me"))
    if not user_is:
        raise credentials_exception
    return user
