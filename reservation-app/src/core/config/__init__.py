"""Packages for config module."""

from .app import settings
from .email import email_connection

__all__ = ["email_connection", "settings"]
