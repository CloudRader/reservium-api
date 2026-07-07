"""Logging configuration."""

import logging
from typing import Literal

from pydantic import BaseModel

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-4d %(levelname)-7s - %(message)s"
)


class LoggingConfig(BaseModel):
    """Config for logging."""

    LOG_LEVEL: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    LOG_FORMAT: str = LOG_DEFAULT_FORMAT
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    @property
    def LOG_CONFIG(self) -> dict:  # noqa: N802
        """Returns a dictionary-compatible configuration for Python's logging module."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.LOG_FORMAT,
                    "datefmt": self.DATE_FORMAT,
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                },
            },
            "root": {
                "handlers": ["default"],
                "level": self.LOG_LEVEL.upper(),
            },
        }

    @property
    def LOG_LEVEL_VALUE(self) -> int:  # noqa: N802
        """
        Converts the LOG_LEVEL string to its corresponding integer value.

        As expected by the logging module.
        """
        return logging.getLevelNamesMapping()[self.LOG_LEVEL.upper()]
