"""
Module to run FastAPI application, where API routers are connecting application to API modules.
In other words it is an entry point of the application.
"""
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api import users, events, calendars, mini_services, reservation_services, \
    fastapi_docs, emails, BaseAppException, app_exception_handler, access_card_system
from core import settings
# import os
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # for local testing


# pylint: disable=unused-argument
# reason: Startup_event require FastAPI.
@asynccontextmanager
async def startup_event(fast_api_app: FastAPI):
    """
    Is called on the application startup, before it is ready to accept requests.
    Is used for app initialization, like here it is creating db tables if they are not created.
    """
    print(f"Starting {settings.APP_NAME}.")
    yield
    print(f"Shutting down {settings.APP_NAME}.")


# pylint: enable=unused-argument


app: FastAPI = FastAPI(
    title=fastapi_docs.NAME,
    description=fastapi_docs.DESCRIPTION,
    version=fastapi_docs.VERSION,
    openapi_tags=fastapi_docs.get_tags_metadata(),
    lifespan=startup_event
)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(reservation_services.router)
app.include_router(calendars.router)
app.include_router(mini_services.router)
app.include_router(emails.router)
app.include_router(access_card_system.router)

app.add_exception_handler(BaseAppException, app_exception_handler)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://develop.reservation.buk.cvut.cz", "https://reservation.buk.cvut.cz",
                   "https://is.buk.cvut.cz"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app",
                host=settings.APP_SERVER_HOST,
                port=settings.APP_SERVER_PORT,
                reload=settings.APP_SERVER_USE_RELOAD,
                proxy_headers=settings.APP_SERVER_USE_PROXY_HEADERS,
                # ssl_keyfile="certification/key.pem",  # for local testing
                # ssl_certfile="certification/cert.pem"
                )
