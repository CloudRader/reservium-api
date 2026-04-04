"""Entry point for running the FastAPI application using Uvicorn or Gunicorn."""

import uvicorn
from core import settings


def uvicorn_run():
    """Run the FastAPI application using Uvicorn."""
    uvicorn.run(
        "main:app",
        host=settings.RUN.SERVER_HOST,
        port=settings.RUN.SERVER_PORT,
        reload=settings.RUN.SERVER_USE_RELOAD,
        proxy_headers=settings.RUN.SERVER_USE_PROXY_HEADERS,
        log_config=settings.LOGGING.LOG_CONFIG,
    )
