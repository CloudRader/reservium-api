"""
Main configuration settings for the Reservium application.

Aggregates all sub-configurations into a unified settings registry.
"""

from core.config.app import ApplicationConfig
from core.config.database import DatabaseConfig
from core.config.email import MailConfig
from core.config.google import GoogleConfig
from core.config.logging import LoggingConfig
from core.config.openid import OpenIdConfig
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application-wide settings registry.

    Loads and orchestrates sub-configuration sections from environment variables.
    """

    app: ApplicationConfig = Field(default_factory=ApplicationConfig)
    log: LoggingConfig = Field(default_factory=LoggingConfig)

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    openid: OpenIdConfig = Field(default_factory=OpenIdConfig)  # type: ignore[call-arg]
    google: GoogleConfig = Field(default_factory=GoogleConfig)  # type: ignore[call-arg]
    mail: MailConfig = Field(default_factory=MailConfig)  # type: ignore[call-arg]


settings = Settings()  # type: ignore[call-arg] # reason: Pydantic handles attribute initialization
