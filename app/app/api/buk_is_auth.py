"""
API controllers for authorisation in IS - Information System of the Buben club.
"""
from api import utils
from fastapi import FastAPI, APIRouter, Query
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse

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
async def callback(code: str = Query(..., description="OAuth2 authorization code")):
    await exchange_code_for_token(code)

    return {"message": "Authorization successful!"}


async def exchange_code_for_token(code: str):
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

    # Save the token to a file
    with open("token.txt", "w") as token_file:
        token_file.write(response_data.get("access_token", ""))

    return response_data.get("access_token", "")
