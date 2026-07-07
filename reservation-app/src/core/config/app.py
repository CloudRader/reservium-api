"""Config."""

from core.config.database import DatabaseConfig
from core.config.email import MailConfig
from core.config.google import GoogleConfig
from core.config.logging import LoggingConfig
from core.config.openid import OpenIdConfig
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    """Config for running application."""

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_USE_RELOAD: bool = False
    SERVER_USE_PROXY_HEADERS: bool = False
    WORKERS: int = 1
    TIMEOUT: int = 900


class Settings(BaseSettings):
    """Settings class."""

    APP_NAME: str = "Reservation System"
    ORGANIZATION_NAME: str = "Organization Name"

    RUN: RunConfig = RunConfig()
    LOGGING: LoggingConfig = LoggingConfig()
    DB: DatabaseConfig
    MAIL: MailConfig
    OPENID: OpenIdConfig
    GOOGLE: GoogleConfig

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=True,
        env_nested_delimiter="__",
        env_file=".env",
    )


settings = Settings()  # type: ignore[call-arg] # reason: Pydantic handles attribute initialization
