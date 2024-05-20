"""
API controllers for authorisation in IS - Information System of the Buben club.
"""
from api import utils
from typing import Annotated
from fastapi import FastAPI, APIRouter, Query, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from services import UserService
from api import exchange_code_for_token, client_id, redirect_uri

app = FastAPI()

router = APIRouter(
    prefix='/auth_is',
    tags=[utils.fastapi_docs.AUTHORISATION_TAG["name"]]
)

# OAuth 2.0 Authorization Code flow configuration
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://is.buk.cvut.cz/oauth/authorize?client_id={client_id}"
                     f"&response_type=code&redirect_uri={redirect_uri}",
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
    print("Control!")
    await exchange_code_for_token(user_service, code)
    # TODO return name and surname to frontend
    return {"message": "Authorization successful!"}
