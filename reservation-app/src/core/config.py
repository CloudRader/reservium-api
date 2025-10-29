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
    USE_GUNICORN: bool = False
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


class SpiceDbConfig(BaseModel):
    """Config for SpiceDb."""

    SERVER_URL: str
    CLIENT_SECRET: str


class GoogleConfig(BaseModel):
    """Config for google."""

    CLIENT_ID: str
    PROJECT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URIS: list[str] = ["http://localhost"]
    SCOPES: list[str] = ["https://www.googleapis.com/auth/calendar"]
    AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"


class DormitoryAccessSystemConfig(BaseModel):
    """Config for dormitory access system."""

    API_KEY: str
    API_URL: str = "https://agata-new.suz.cvut.cz/pristupAPI/api.php"


class Settings(BaseSettings):
    """Settings class."""

    APP_NAME: str = "Reservation System"
    ORGANIZATION_NAME: str = "Organization Name"

    RUN: RunConfig = RunConfig()
    LOGGING: LoggingConfig = LoggingConfig()
    DB: DatabaseConfig
    MAIL: MailConfig
    KEYCLOAK: KeycloakConfig
    SPICEDB: SpiceDbConfig
    GOOGLE: GoogleConfig
    DORMITORY_ACCESS_SYSTEM: DormitoryAccessSystemConfig

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_nested_delimiter="__",
        env_file=get_env_file_path([".env.template", ".env"]),
    )


settings = Settings()  # type: ignore[call-arg] # reason: Pydantic handles attribute initialization
