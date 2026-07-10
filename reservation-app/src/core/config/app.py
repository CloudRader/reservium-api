"""
Application-wide general running and server configurations.

Defines host, port, reload options, and worker processes for the API server.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationConfig(BaseSettings):
    """
    General configuration for the application environment and HTTP server.

    Loads values from environment variables prefixed with `APP_` or defaults,
    defining basic properties like application name, organization name,
    and Uvicorn server runner settings.
    """

    name: str = Field(default="Reservium", validation_alias="APP_NAME")
    organization_name: str = Field(default="CloudRader", validation_alias="APP_ORGANIZATION_NAME")

    server_host: str = Field(default="0.0.0.0", validation_alias="APP_SERVER_HOST")
    server_port: int = Field(default=8000, validation_alias="APP_SERVER_PORT")
    server_use_reload: bool = Field(default=False, validation_alias="APP_SERVER_USE_RELOAD")
    server_use_proxy_headers: bool = Field(
        default=False, validation_alias="APP_SERVER_USE_PROXY_HEADERS"
    )
    workers: int = Field(default=1, validation_alias="APP_WORKERS")
    timeout: int = Field(default=900, validation_alias="APP_TIMEOUT")

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=True,
        env_file=".env",
    )
