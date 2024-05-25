"""
Module to run FastAPI application, where API routers are connecting application to API modules.
In other words it is an entry point of the application.
"""
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import buk_is_auth, events, calendars, mini_services, \
    MethodNotAllowedException, EntityNotFoundException, NotImplementedException, \
    fastapi_docs, method_not_allowed_exception_handler, \
    entity_not_found_exception_handler, not_implemented_exception_handler
from core import settings
from db import init_db


# pylint: disable=unused-argument
# reason: Startup_event require FastAPI.
@asynccontextmanager
async def startup_event(fast_api_app: FastAPI):
    """
    Is called on the application startup, before it is ready to accept requests.
    Is used for app initialization, like here it is creating db tables if they are not created.
    """
    print(f"Starting {settings.APP_NAME}.")
    init_db()
    yield
    print(f"Shutting down {settings.APP_NAME}.")


# pylint: enable=unused-argument


app = FastAPI(
    title=fastapi_docs.NAME,
    description=fastapi_docs.DESCRIPTION,
    version=fastapi_docs.VERSION,
    openapi_tags=fastapi_docs.get_tags_metadata(),
    lifespan=startup_event
)
app.include_router(buk_is_auth.router)
app.include_router(events.router)
app.include_router(calendars.router)
app.include_router(mini_services.router)

app.add_exception_handler(
    MethodNotAllowedException, method_not_allowed_exception_handler
)
app.add_exception_handler(
    EntityNotFoundException, entity_not_found_exception_handler
)
app.add_exception_handler(
    NotImplementedException, not_implemented_exception_handler
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rezervace.buk.cvut.cz:80"],
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
                ssl_keyfile="certification/key.pem",
                ssl_certfile="certification/cert.pem")
