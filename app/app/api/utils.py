"""
Utils for API.
"""
import httpx
from fastapi.responses import RedirectResponse
from fastapi import Depends, Query
from schemas import UserIS, UserUpdate, UserCreate
from services import UserService
from typing import Annotated
from schemas.user_is import RoleList

client_id = "e36219f8fdd7619dfa80754aa17c47e38c04e4407d37c26e48058531c82b18c1"
client_secret = "44218c6184e21ee1e679586bcbe8d5b1727d6a771c6619a46aa821fe1eff4e98"
redirect_uri = "https://10.0.52.106:8000/auth_is/login/callback"


async def get_request(token: str, request: str, user_service: Annotated[UserService, Depends(UserService)]):
    info_endpoint = "https://api.is.buk.cvut.cz/v1/" + request

    async with httpx.AsyncClient() as client:
        response = await client.get(info_endpoint, headers={"Authorization": f"Bearer {token}"})

        if response.status_code == 401:
            # code: str = Query(..., description="OAuth2 authorization code")
            # data = exchange_code_for_token(user_service, code)

            return RedirectResponse(url="https://10.0.52.106:8000/auth_is/login")

        response.raise_for_status()

        response_data = response.json()

    return response_data


async def exchange_code_for_token(user_service: Annotated[UserService, Depends(UserService)],
                                  code: str):
    token_endpoint = "https://is.buk.cvut.cz/oauth/token"
    client_credentials = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_endpoint, data=client_credentials)
        response_data = response.json()

        token = response_data.get("access_token", "")
        response_user = await client.get("https://api.is.buk.cvut.cz/v1/users/me",
                                         headers={"Authorization": f"Bearer {token}"})
        response_data_user = response_user.json()

    user_data = UserIS(**response_data_user)
    roles = RoleList(roles=await get_request(token, "/user_roles/mine", user_service)).roles
    user_service.create_user(user_data, roles, token)

    return response_data.get("access_token", "")


class FastApiDocs:
    """Information for fastapi documentation."""
    NAME = "Reservation System of the Buben Club"
    DESCRIPTION = """Reservation System of the Buben Club API is a **REST API** that offers you an access to
    our application!"""
    VERSION = "1.0.0"
    AUTHORISATION_TAG = {
        "name": "users",
        "description": "Authorisation in IS.",
    }

    def get_tags_metadata(self):
        """Get tags metadata."""
        return [
            self.AUTHORISATION_TAG,
        ]


fastapi_docs = FastApiDocs()

# pylint: enable=too-few-public-methods
