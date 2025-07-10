"""Config."""

from pydantic import PostgresDsn, BaseModel
from pydantic_settings import BaseSettings
from .utils import get_env_file_path


class RunConfig(BaseModel):
    """Config for running application."""

    SERVER_HOST: str
    SERVER_PORT: int
    SERVER_USE_RELOAD: bool
    SERVER_USE_PROXY_HEADERS: bool


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
    def POSTGRES_DATABASE_URI(self) -> str:  # pylint: disable=invalid-name
        """
        Assemble database connection URI.
        """
        return str(
            PostgresDsn.build(
                scheme=self.SQLALCHEMY_SCHEME,
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
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

    SCOPES: str
    CLIENT_ID: str
    PROJECT_ID: str
    CLIENT_SECRET: str


class DormitoryAccessSystemConfig(BaseModel):
    """Config for dormitory access system."""

    API_KEY: str
    API_URL: str


class Settings(BaseSettings):
    """Settings class."""

    APP_NAME: str
    SECRET_KEY: str

    RUN: RunConfig
    DB: DatabaseConfig
    MAIL: MailConfig
    IS: ISConfig
    GOOGLE: GoogleConfig
    DORMITORY_ACCESS_SYSTEM: DormitoryAccessSystemConfig

    # pylint: disable=too-few-public-methods
    # reason: special class for pydantic configuration.
    class Config:
        """Config class."""

        case_sensitive = True
        env_settings = True
        env_nested_delimiter = "__"
        env_file = get_env_file_path([".env.template", ".env"])

    # pylint: enable=too-few-public-methods


settings = Settings()  # type: ignore[call-arg] # reason: Pydantic handles attribute initialization
