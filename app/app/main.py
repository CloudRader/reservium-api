"""
Module to run FastAPI application, where API routers are connecting application to API modules.
In other words it is an entry point of the application.
"""

import logging
from core import settings, uvicorn_run, guvicorn_run, create_app


logging.basicConfig(
    level=settings.LOGGING.LOG_LEVEL_VALUE,
    format=settings.LOGGING.LOG_FORMAT,
)

app = create_app()

if __name__ == "__main__":
    if settings.RUN.USE_GUNICORN:
        guvicorn_run(app)
    uvicorn_run()
