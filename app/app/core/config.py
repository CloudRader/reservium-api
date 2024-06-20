"""Config."""
from typing import Dict, Any
from pydantic import validator, PostgresDsn
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

    TEST_DATABASE_URI: str

    # pylint: disable=no-self-argument
    # reason: pydantic validator doesn't work with self argument.
    @validator("POSTGRES_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, value: str | None, values: Dict[str, Any]) -> str:
        """Assemble database connection URI.

        :param value: Value to set URI with.
        :param values: Values to build URI from, if value is None.
        """
        if isinstance(value, str):
            return value
        return str(PostgresDsn.build(  # pylint: disable=no-member
            scheme=values.get("SQLALCHEMY_SCHEME", "postgresql"),
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f'{values.get("POSTGRES_DB")}'
        ))

    # pylint: enable=no-self-argument

    # pylint: disable=too-few-public-methods
    # reason: special class for pydantic configuration.
    class Config:
        """Config class."""
        case_sensitive = True
        env_settings = True
        env_file = get_env_file_path([".env.dev", ".env"])

    # pylint: enable=too-few-public-methods


settings = Settings()  # type: ignore[call-arg] # reason: Pydantic handles attribute initialization
