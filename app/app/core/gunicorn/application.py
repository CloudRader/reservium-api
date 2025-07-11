"""
Custom Gunicorn application wrapper for FastAPI.
"""

from fastapi import FastAPI
from gunicorn.app.base import BaseApplication


class Application(BaseApplication):
    """
    Gunicorn application wrapper for FastAPI.
    """

    def __init__(
        self,
        application: FastAPI,
        options: dict | None = None,
    ):
        """
        Initialize the Gunicorn application with a FastAPI instance and optional config.
        """
        self.options = options or {}
        self.application = application
        super().__init__()

    def init(self, parser, opts, args):
        """
        Override required abstract method from BaseApplication.
        """

    def load(self):
        """
        Return the FastAPI application instance to be run by Gunicorn.
        """
        return self.application

    @property
    def config_options(self) -> dict:
        """
        Filter and return valid Gunicorn config options.
        """
        return {
            # pair
            k: v
            # for each option
            for k, v in self.options.items()
            # not empty key / value
            if k in self.cfg.settings and v is not None
        }

    def load_config(self):
        """
        Load the valid Gunicorn config options into the Gunicorn configuration object.
        """
        for key, value in self.config_options.items():
            self.cfg.set(key.lower(), value)
