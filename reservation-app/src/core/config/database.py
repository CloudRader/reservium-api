"""
Database configuration settings for PostgreSQL and SQLAlchemy.

Provides settings classes for secure connection credentials and ORM
engine configuration (connection pooling, statement logging, etc.).
"""

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    """
    Configuration settings for the physical PostgreSQL database resource.

    Validates and maps server address, port, username, password, and database name
    directly from their respective uppercase environment variables (e.g. `POSTGRES_USER`).
    """

    user: str = Field(validation_alias="POSTGRES_USER")
    password: SecretStr = Field(validation_alias="POSTGRES_PASSWORD")
    db: str = Field(validation_alias="POSTGRES_DB")
    server: str = Field(default="localhost", validation_alias="POSTGRES_SERVER")
    port: int = Field(default=5432, validation_alias="POSTGRES_PORT")

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=True,
        env_file=".env",
    )


class DatabaseConfig(BaseSettings):
    """
    SQLAlchemy Database Client configurations.

    Orchestrates the connection pool settings, naming conventions for schema migrations,
    statement echo logging flags, and nests database server credentials. Exposes a
    property to assemble the fully validated database connection URI.
    """

    scheme: str = Field(default="postgresql+asyncpg", validation_alias="DB_SQLALCHEMY_SCHEME")
    echo: bool = Field(default=False, validation_alias="DB_ECHO")
    echo_pool: bool = Field(default=False, validation_alias="DB_ECHO_POOL")
    pool_size: int = Field(default=50, validation_alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, validation_alias="DB_MAX_OVERFLOW")
    pool_pre_ping: bool = Field(default=True, validation_alias="DB_POOL_PRE_PING")
    pool_recycle: int = Field(default=3600, validation_alias="DB_POOL_RECYCLE")

    # Nesting the credentials
    credentials: PostgresConfig = Field(default_factory=PostgresConfig)  # type: ignore[arg-type]

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def postgres_database_uri(self) -> str:
        """Assemble database connection URI."""
        return str(
            PostgresDsn.build(
                scheme=self.scheme,
                username=self.credentials.user,
                password=self.credentials.password.get_secret_value(),
                host=self.credentials.server,
                port=self.credentials.port,
                path=self.credentials.db,
            )
        )

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=True,
        env_file=".env",
    )
