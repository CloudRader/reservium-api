"""
Module to run FastAPI application, where API routers are connecting application to API modules.

In other words it is an entry point of the application.
"""

import logging

from core.bootstrap import create_app, uvicorn_run
from core.config import settings

logging.basicConfig(
    level=settings.log.level_value,
    format=settings.log.format,
)

app = create_app()

if __name__ == "__main__":
    uvicorn_run()
