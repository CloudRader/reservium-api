"""
API controllers for authorisation in IS - Information System of the Buben club.
"""
from api import utils
from typing import Annotated
from fastapi import FastAPI, APIRouter, Query, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from schemas import UserIS, UserUpdate, UserCreate
from services import UserService

import httpx

app = FastAPI()

router = APIRouter(
    prefix='/auth_is',
    tags=[utils.fastapi_docs.AUTHORISATION_TAG["name"]]
)

client_id = "e36219f8fdd7619dfa80754aa17c47e38c04e4407d37c26e48058531c82b18c1"
client_secret = "44218c6184e21ee1e679586bcbe8d5b1727d6a771c6619a46aa821fe1eff4e98"
redirect_uri = "https://10.0.52.106:8000/auth_is/login/callback"

# OAuth 2.0 Authorization Code flow configuration
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://is.buk.cvut.cz/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}",
    tokenUrl="https://is.buk.cvut.cz/oauth/token",
    auto_error=False,
)


@router.get("/login")
async def login():
    # Manually construct the authorization URL
    authorization_url = (
        f"https://is.buk.cvut.cz/oauth/authorize?client_id={client_id}"
        "&response_type=code&scope=location"  # Include the "location" scope
        f"&redirect_uri={redirect_uri}"
    )

    return RedirectResponse(url=authorization_url)


@router.get("/login/callback")
async def callback(user_service: Annotated[UserService, Depends(UserService)],
                   code: str = Query(..., description="OAuth2 authorization code")):
    await exchange_code_for_token(user_service, code)

    return {"message": "Authorization successful!"}


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
    user = user_service.get_by_username(user_data.username)

    if user:
        user_update = UserUpdate(
            user_token=token
        )
        user_service.update(user.uuid, user_update)
    else:
        user_create = UserCreate(
            username=user_data.username,
            user_token=token,
            role="club member"
        )
        user_service.create(user_create)

    return response_data.get("access_token", "")
