"""App factory module for the FastAPI application."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from core.bootstrap.providers import create_providers
from core.config import settings
from core.ioc.di import get_providers
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def startup_event(app: FastAPI) -> AsyncGenerator[None]:
    """
    Startup and shutdown lifecycle event handler.

    This function is triggered when the FastAPI app starts and stops.
    It logs startup and shutdown messages.

    :param fast_api_app: The FastAPI application instance.
    """
    app.state.providers = create_providers()
    logger.info("Starting %s.", settings.app.name)
    yield
    logger.info("Shutting down %s.", settings.app.name)


def create_app() -> FastAPI:
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
    from core.bootstrap.docs import fastapi_docs
    from core.bootstrap.exceptions import register_errors_handlers

    app = FastAPI(
        title=fastapi_docs.NAME,
        description=fastapi_docs.DESCRIPTION,
        version=fastapi_docs.VERSION,
        openapi_tags=fastapi_docs.get_tags_metadata(),
        lifespan=startup_event,
    )

    container: AsyncContainer = make_async_container(*get_providers())
    setup_dishka(container, app)

    app.include_router(router)

    register_errors_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://develop.reservation.buk.cvut.cz",
            "https://reservation.buk.cvut.cz",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
