"""
Logging configuration options for application monitoring.

Defines formats, timestamp parameters, and handlers for stdio logging output.
"""

import logging
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseSettings):
    """
    Configuration settings for application logging handlers and formats.

    Loads custom formatting strings and date-time output preferences from
    environment variables prefixed with `LOG_`. Provides standard logging config maps.
    """

    level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    format: str = Field(
        default="[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-4d %(levelname)-7s - %(message)s",
        validation_alias="LOG_FORMAT",
    )
    date_format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        validation_alias="LOG_DATE_FORMAT",
    )

    @property
    def config(self) -> dict:
        """Returns a dictionary-compatible configuration for Python's logging module."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.format,
                    "datefmt": self.date_format,
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
                "level": self.level.upper(),
            },
        }

    @property
    def level_value(self) -> int:
        """
        Converts the LOG_LEVEL string to its corresponding integer value.

        As expected by the logging module.
        """
        return logging.getLevelNamesMapping()[self.level.upper()]

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=True,
        env_file=".env",
    )
