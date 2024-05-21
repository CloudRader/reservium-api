"""
API controllers for authorisation in IS - Information System of the Buben club.
"""
from api import utils
from typing import Annotated, Any
from fastapi import FastAPI, APIRouter, Query, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from services import UserService
from api import exchange_code_for_token, client_id, redirect_uri
from schemas import UserIS

app = FastAPI()

router = APIRouter(
    prefix='/auth_is',
    tags=[utils.fastapi_docs.AUTHORISATION_TAG["name"]]
)

# OAuth 2.0 Authorization Code flow configuration
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://is.buk.cvut.cz/oauth/authorize?client_id={client_id}"
                     f"&response_type=code&scope=location"
                     f"&redirect_uri={redirect_uri}",
    tokenUrl="https://is.buk.cvut.cz/oauth/token",
    auto_error=False,
)


@router.get("/login")
async def login():
    """
    Authenticate a user, construct authorization URL and redirect to authorization page of IS.
    """
    authorization_url = (
        f"https://is.buk.cvut.cz/oauth/authorize?client_id={client_id}"
        "&response_type=code&scope=location"  # Include the "location" scope
        f"&redirect_uri={redirect_uri}"
    )

    return RedirectResponse(url=authorization_url)


@router.get("/login/callback",
            response_model=UserIS
            )
async def callback(user_service: Annotated[UserService, Depends(UserService)],
                   code: str = Query(..., description="OAuth2 authorization code")) -> Any:
    """
    Callback link after authorization on IS.

    :param user_service: User service
    :param code: Code received at authorization, needed to get the user token.

    :return: Authorized  User schema.
    """
    user = await exchange_code_for_token(user_service, code)
    return user
