"""App factory module for the FastAPI application."""

import logging
from contextlib import asynccontextmanager

from core import settings
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def startup_event(fast_api_app: FastAPI):  # noqa: ARG001
    """
    Startup and shutdown lifecycle event handler.

    This function is triggered when the FastAPI app starts and stops.
    It logs startup and shutdown messages.

    :param fast_api_app: The FastAPI application instance.
    """
    logger.info("Starting %s.", settings.APP_NAME)
    yield
    logger.info("Shutting down %s.", settings.APP_NAME)


def create_app():
    """
    Create and configure the FastAPI app.

    This sets up:
    - Application metadata
    - Routers for API modules
    - Custom exception handler
    - Middleware (sessions, CORS)

    :return: A fully configured FastAPI app instance.
    """
    from api.routers import router
    from core.application.docs import fastapi_docs
    from core.application.exceptions import BaseAppError, app_exception_handler

    app = FastAPI(
        title=fastapi_docs.NAME,
        description=fastapi_docs.DESCRIPTION,
        version=fastapi_docs.VERSION,
        openapi_tags=fastapi_docs.get_tags_metadata(),
        lifespan=startup_event,
        default_response_class=ORJSONResponse,
    )

    app.include_router(router)

    app.add_exception_handler(BaseAppError, app_exception_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://develop.reservation.buk.cvut.cz",
            "https://reservation.buk.cvut.cz",
            "https://is.buk.cvut.cz",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    return app
