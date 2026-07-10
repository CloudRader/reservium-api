"""Entry point for running the FastAPI application using Uvicorn or Gunicorn."""

import uvicorn
from core.config import settings


def uvicorn_run():
    """Run the FastAPI application using Uvicorn."""
    uvicorn.run(
        "main:app",
        host=settings.app.server_host,
        port=settings.app.server_port,
        reload=settings.app.server_use_reload,
        proxy_headers=settings.app.server_use_proxy_headers,
        log_config=settings.log.config,
    )
