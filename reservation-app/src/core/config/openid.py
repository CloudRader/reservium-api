"""
OpenID Connect (OIDC) identity provider configuration settings.

Defines credentials, URLs, and metadata endpoints for OIDC integration.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenIdConfig(BaseSettings):
    """
    Configuration settings for Single Sign-On (SSO) integration.

    Loads and maps connection details (client ID, client secret, and server URLs)
    directly from their respective uppercase environment variables (e.g. `OPENID_CLIENT_ID`).
    """

    client_name: str = Field(validation_alias="OPENID_CLIENT_NAME")
    client_id: str = Field(validation_alias="OPENID_CLIENT_ID")
    client_secret: SecretStr = Field(validation_alias="OPENID_CLIENT_SECRET")
    auth_url: str = Field(validation_alias="OPENID_AUTH_URL")
    token_url: str = Field(validation_alias="OPENID_TOKEN_URL")
    metadata_url: str = Field(validation_alias="OPENID_METADATA_URL")
    scopes: str = Field(default="openid email profile", validation_alias="OPENID_SCOPES")

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=True,
        env_file=".env",
    )
