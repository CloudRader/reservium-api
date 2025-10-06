"""API controllers for authorisation in IS(Information System of the club)."""

from typing import Annotated

from core import settings
from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2AuthorizationCodeBearer
from integrations.keycloak import KeycloakAuthService
from services import UserService

app = FastAPI()

router = APIRouter()


http_bearer = HTTPBearer()


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.KEYCLOAK.SERVER_URL}/realms/{settings.KEYCLOAK.REALM}"
    f"/protocol/openid-connect/auth?scope=openid roles",
    tokenUrl=f"{settings.KEYCLOAK.SERVER_URL}/realms/{settings.KEYCLOAK.REALM}/protocol/openid-connect/token",
)


@router.get(
    "/token-swagger",
    status_code=status.HTTP_200_OK,
)
async def get_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Retrieve the OAuth2 access token from the authorization code flow.

    This endpoint is intended for use with Swagger UI. When a user
    authenticates via Keycloak through the Swagger interface,
    FastAPI's `OAuth2AuthorizationCodeBearer` dependency automatically
    handles the OAuth2 code exchange and injects the resulting access token.
    """
    return {"access_token": token}


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login(
    user_service: Annotated[UserService, Depends(UserService)],
    keycloak_service: Annotated[KeycloakAuthService, Depends(KeycloakAuthService)],
    token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
):
    """Authenticate a user."""
    user_info = await keycloak_service.get_user_info(token.credentials)
    user = await user_service.create_user(user_info)

    return user


@router.get("/logout")
async def logout():
    """
    Clean session of the current user.

    :return: Message.
    """
    # TODO with token flow
    return {"message": "Logged out"}
