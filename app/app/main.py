"""
Module to run FastAPI application, where API routers are connecting application to API modules.
In other words it is an entry point of the application.
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from api import buk_is_auth, events, calendars, \
    MethodNotAllowedException, EntityNotFoundException, NotImplementedException, \
    method_not_allowed_exception_handler, entity_not_found_exception_handler, not_implemented_exception_handler
from core import settings
from db import init_db


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


app = FastAPI(lifespan=startup_event)

app.include_router(buk_is_auth.router)
app.include_router(events.router)
app.include_router(calendars.router)

app.add_exception_handler(
    MethodNotAllowedException, method_not_allowed_exception_handler
)
app.add_exception_handler(
    EntityNotFoundException, entity_not_found_exception_handler
)
app.add_exception_handler(
    NotImplementedException, not_implemented_exception_handler
)

if __name__ == "__main__":
    uvicorn.run(app, host="10.0.52.106", port=8000,
                ssl_keyfile="certification/key.pem", ssl_certfile="certification/cert.pem")
