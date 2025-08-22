"""API controllers for authorisation in IS(Information System of the club)."""

from typing import Annotated, Any

from api import authenticate_user
from core.application.exceptions import ERROR_RESPONSES
from fastapi import APIRouter, Depends, FastAPI, Query, status
from fastapi.responses import RedirectResponse
from integrations.information_system import IsAuthService, IsService
from services import UserService

app = FastAPI()

router = APIRouter()


@router.get(
    "/login_dev",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def login_local_dev(
    is_auth_service: Annotated[IsAuthService, Depends(IsAuthService)],
):
    """
    Authenticate a user, construct authorization URL and redirect to authorization page of IS.

    This endpoint for local authorization.
    """
    return RedirectResponse(await is_auth_service.generate_is_oauth_redirect_uri())


@router.get(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login(
    is_auth_service: Annotated[IsAuthService, Depends(IsAuthService)],
):
    """Authenticate a user, construct authorization URL and sent it for authorization."""
    return await is_auth_service.generate_is_oauth_redirect_uri()


@router.get(
    "/callback",
    responses=ERROR_RESPONSES["401"],
    status_code=status.HTTP_200_OK,
)
async def callback(
    user_service: Annotated[UserService, Depends(UserService)],
    is_auth_service: Annotated[IsAuthService, Depends(IsAuthService)],
    is_service: Annotated[IsService, Depends(IsService)],
    code: str = Query(...),
) -> Any:
    """
    Handle callback after authorization on IS.

    :param user_service: UserLite service.
    :param is_auth_service: IsAuthService service.
    :param is_service: IsService service.
    :param code: Code received, needed to get the user token.

    :return: Authorized  UserLite schema.
    """
    token_response = await is_auth_service.get_token_response(code)

    user = await authenticate_user(user_service, is_service, token_response.access_token)

    return {
        "username": user.username,
        "token_type": token_response.token_type,
        "access_token": token_response.access_token,
        "expires_in": token_response.expires_in,
        "scope": token_response.scope,
    }


@router.get("/logout")
async def logout():
    """
    Clean session of the current user.

    :return: Message.
    """
    # TODO with token flow
    return {"message": "Logged out"}
