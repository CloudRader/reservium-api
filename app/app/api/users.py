"""
API controllers for authorisation in IS(Information System of the Buben club)
and users itself.
"""
from typing import Annotated, Any, List
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from services import UserService
from api import authenticate_user, fastapi_docs, get_oauth_session, get_current_user, \
    modify_url_scheme
from schemas import User
from core import settings

app = FastAPI()

router = APIRouter(
    prefix='/users',
    tags=[fastapi_docs.AUTHORISATION_TAG["name"]]
)


@router.get("/login_dev")
async def login_local_dev(request: Request):
    """
    Authenticate a user, construct authorization URL and redirect to authorization page of IS.
    This endpoint for local authorization.
    """
    authorization_url = (
        f"{settings.IS_OAUTH}/authorize?client_id={settings.CLIENT_ID}"
        "&response_type=code&scope=location"  # Include the "location" scope
    )
    oauth = get_oauth_session()
    authorization_url, state = oauth.authorization_url(authorization_url)
    request.session['oauth_state'] = state
    return RedirectResponse(authorization_url)  # for local dev


@router.get("/login")
async def login(request: Request):
    """
    Authenticate a user, construct authorization URL and sent it for authorization.
    """
    authorization_url = (
        f"{settings.IS_OAUTH}/authorize?client_id={settings.CLIENT_ID}"
        "&response_type=code&scope=location"  # Include the "location" scope
    )
    oauth = get_oauth_session()
    authorization_url, state = oauth.authorization_url(authorization_url)
    request.session['oauth_state'] = state
    return authorization_url


@router.get("/callback")
async def callback(
        user_service: Annotated[UserService, Depends(UserService)],
        request: Request
) -> Any:
    """
    Callback link after authorization on IS.

    :param user_service: User service.
    :param request: Request received, needed to get the user token.

    :return: Authorized  User schema.
    """
    oauth = get_oauth_session()

    authorization_response_url = modify_url_scheme(str(request.url), 'https')

    try:
        token = oauth.fetch_token(
            settings.IS_OAUTH_TOKEN,
            client_secret=settings.CLIENT_SECRET,
            authorization_response=authorization_response_url
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"There's some problem with getting token. "
                   f"Control this url: {authorization_response_url}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    request.session['oauth_token'] = token

    user = await authenticate_user(user_service, token['access_token'])
    request.session['user_username'] = user.username

    return {"username": user.username, "token_type": "bearer"}


@router.get("/me",
            response_model=User)
async def get_user(
        current_user: Annotated[User, Depends(get_current_user)]
) -> Any:
    """
     Get currently authenticated user.

     :param current_user: Current user.

     :return: Current user.
     """
    return current_user


@router.get("/",
            response_model=List[User])
async def get_all_users(
        user_service: Annotated[UserService, Depends(UserService)]
) -> Any:
    """
     Get all users.

     :param user_service: User service.

     :return: All users in database.
     """
    users = await user_service.get_all()
    if not users:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "No users in db."
            }
        )
    return users


@router.get("/logout")
async def logout(request: Request):
    """
    Clean session of the current user.

    :param request: Request received.

    :return: Message.
    """
    request.session.clear()
    return {"message": "Logged out"}
