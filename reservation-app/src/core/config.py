"""Config."""

import logging
from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from .utils import get_env_file_path

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-4d %(levelname)-7s - %(message)s"
)


class RunConfig(BaseModel):
    """Config for running application."""

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    SERVER_USE_RELOAD: bool = False
    SERVER_USE_PROXY_HEADERS: bool = False
    WORKERS: int = 1
    TIMEOUT: int = 900


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

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_SCHEME: str = "postgresql+asyncpg"

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
    FROM_NAME: str
    PORT: int = 587
    SERVER: str = "smtp.gmail.com"
    TLS: bool = True
    SSL: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    SENT_DORMITORY_HEAD: bool = False
    DORMITORY_HEAD_EMAIL: str = ""


class KeycloakConfig(BaseModel):
    """Config for Keycloak."""

    SERVER_URL: str
    REALM: str
    CLIENT_ID: str
    CLIENT_SECRET: str


class GoogleConfig(BaseModel):
    """Config for google."""

    TYPE: str = "service_account"
    PROJECT_ID: str
    PRIVATE_KEY_ID: str
    PRIVATE_KEY: str
    CLIENT_EMAIL: str
    CLIENT_ID: str
    AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    CLIENT_X509_CERT_URL: str
    SCOPES: list[str] = ["https://www.googleapis.com/auth/calendar"]

    @property
    def INFO(self) -> dict:  # noqa: N802
        """Return service account credentials in Google-compatible format."""
        return {
            "type": self.TYPE,
            "project_id": self.PROJECT_ID,
            "private_key_id": self.PRIVATE_KEY_ID,
            "private_key": self.PRIVATE_KEY.replace("\\n", "\n"),
            "client_email": self.CLIENT_EMAIL,
            "client_id": self.CLIENT_ID,
            "auth_uri": self.AUTH_URI,
            "token_uri": self.TOKEN_URI,
            "auth_provider_x509_cert_url": self.AUTH_PROVIDER_X509_CERT_URL,
            "client_x509_cert_url": self.CLIENT_X509_CERT_URL,
        }


class Settings(BaseSettings):
    """Settings class."""

    APP_NAME: str = "Reservation System"
    ORGANIZATION_NAME: str = "Organization Name"

    RUN: RunConfig = RunConfig()
    LOGGING: LoggingConfig = LoggingConfig()
    DB: DatabaseConfig
    MAIL: MailConfig
    KEYCLOAK: KeycloakConfig
    GOOGLE: GoogleConfig

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_nested_delimiter="__",
        env_file=get_env_file_path([".env"]),
    )


settings = Settings()  # type: ignore[call-arg] # reason: Pydantic handles attribute initialization
