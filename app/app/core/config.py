"""Config."""
from typing import Any
from pydantic import field_validator, PostgresDsn
from pydantic_settings import BaseSettings
from .utils import get_env_file_path


class Settings(BaseSettings):
    """Settings class."""
    APP_NAME: str
    APP_SERVER_HOST: str
    APP_SERVER_PORT: int

    APP_SERVER_USE_RELOAD: bool
    APP_SERVER_USE_PROXY_HEADERS: bool

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    SQLALCHEMY_SCHEME: str
    POSTGRES_DATABASE_URI: PostgresDsn | None = None

    SECRET_KEY: str

    DORMITORY_ACCESS_SYSTEM_API_KEY: str
    DORMITORY_ACCESS_SYSTEM_API_URL: str

    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    IS_SCOPES: str
    IS_OAUTH_TOKEN: str
    IS_OAUTH: str

    GOOGLE_SCOPES: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_PROJECT_ID: str
    GOOGLE_CLIENT_SECRET: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_TLS: bool
    MAIL_SSL: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    TEST_DATABASE_URI: str

    # pylint: disable=no-self-argument
    # reason: pydantic validator doesn't work with self argument.
    # @validator("POSTGRES_DATABASE_URI", pre=True)
    @field_validator("POSTGRES_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, value: str | None, info: Any) -> str:
        """Assemble database connection URI.

        :param value: Value to set URI with.
        :param info: Values to build URI from, if value is None.
        """
        if isinstance(value, str):
            return value
        return str(PostgresDsn.build(  # pylint: disable=no-member
            scheme=info.data.get("SQLALCHEMY_SCHEME", "postgresql+asyncpg"),
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            port=info.data.get("POSTGRES_PORT"),
            path=f'{info.data.get("POSTGRES_DB")}'
        ))

    # pylint: enable=no-self-argument

    # pylint: disable=too-few-public-methods
    # reason: special class for pydantic configuration.
    class Config:
        """Config class."""
        case_sensitive = True
        env_settings = True
        env_file = get_env_file_path([".env.dev", ".env.secret", ".env"])

    # pylint: enable=too-few-public-methods


settings = Settings()  # type: ignore[call-arg] # reason: Pydantic handles attribute initialization
