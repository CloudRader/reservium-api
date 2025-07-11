"""
Entry point for running the FastAPI application using Uvicorn or Gunicorn.
"""

import uvicorn
from fastapi import FastAPI
from core import settings
from core.gunicorn.application import Application
from core.gunicorn.app_options import get_app_options


def guvicorn_run(app: FastAPI):
    """
    Run the FastAPI application using Gunicorn.
    """
    Application(
        application=app,
        options=get_app_options(
            host=settings.RUN.SERVER_HOST,
            port=settings.RUN.SERVER_PORT,
            timeout=settings.RUN.TIMEOUT,
            workers=settings.RUN.WORKERS,
            log_level=settings.LOGGING.LOG_LEVEL,
        ),
    ).run()


def uvicorn_run():
    """
    Run the FastAPI application using Uvicorn.
    """
    uvicorn.run(
        "main:app",
        host=settings.RUN.SERVER_HOST,
        port=settings.RUN.SERVER_PORT,
        reload=settings.RUN.SERVER_USE_RELOAD,
        proxy_headers=settings.RUN.SERVER_USE_PROXY_HEADERS,
        log_config=settings.LOGGING.LOG_CONFIG,
        # ssl_keyfile="certification/key.pem",
        # ssl_certfile="certification/cert.pem",
    )
