"""Config."""

import logging
from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings

from .utils import get_env_file_path

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-4d %(levelname)-7s - %(message)s"
)


class RunConfig(BaseModel):
    """Config for running application."""

    SERVER_HOST: str
    SERVER_PORT: int
    SERVER_USE_RELOAD: bool
    SERVER_USE_PROXY_HEADERS: bool
    USE_GUNICORN: bool
    WORKERS: int
    TIMEOUT: int


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


class DatabaseConfig(BaseModel):
    """Config for db."""

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    SQLALCHEMY_SCHEME: str

    NAMING_CONVENTION: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def POSTGRES_DATABASE_URI(self) -> str:  # noqa: N802
        """Assemble database connection URI."""
        return str(
            PostgresDsn.build(
                scheme=self.SQLALCHEMY_SCHEME,
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            ),
        )


class MailConfig(BaseModel):
    """Config for mail."""

    USERNAME: str
    PASSWORD: str
    PORT: int
    SERVER: str
    FROM_NAME: str
    TLS: bool
    SSL: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool


class ISConfig(BaseModel):
    """Config for IS."""

    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    SCOPES: str
    OAUTH_TOKEN: str
    OAUTH: str


class GoogleConfig(BaseModel):
    """Config for google."""

    CLIENT_ID: str
    PROJECT_ID: str
    AUTH_URI: str
    TOKEN_URI: str
    AUTH_PROVIDER_X509_CERT_URL: str
    CLIENT_SECRET: str
    REDIRECT_URIS: list[str]
    SCOPES: list[str]


class DormitoryAccessSystemConfig(BaseModel):
    """Config for dormitory access system."""

    API_KEY: str
    API_URL: str


class Settings(BaseSettings):
    """Settings class."""

    APP_NAME: str
    CLUB_NAME: str
    SECRET_KEY: str

    RUN: RunConfig
    LOGGING: LoggingConfig = LoggingConfig()
    DB: DatabaseConfig
    MAIL: MailConfig
    IS: ISConfig
    GOOGLE: GoogleConfig
    DORMITORY_ACCESS_SYSTEM: DormitoryAccessSystemConfig

    class Config:
        """Config class."""

        case_sensitive = True
        env_settings = True
        env_nested_delimiter = "__"
        env_file = get_env_file_path([".env.template", ".env"])


settings = Settings()  # type: ignore[call-arg] # reason: Pydantic handles attribute initialization
