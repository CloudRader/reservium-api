"""Packages for core module."""

# ruff: noqa: I001
from .config import settings
from .config_email import email_connection
from .application import uvicorn_run, create_app

__all__ = [
    "create_app",
    "email_connection",
    "settings",
    "uvicorn_run",
]
