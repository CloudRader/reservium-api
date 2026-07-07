"""OpenID configuration."""

from pydantic import BaseModel, SecretStr


class OpenIdConfig(BaseModel):
    """Config for OpenID."""

    CLIENT_NAME: str
    CLIENT_ID: str
    CLIENT_SECRET: SecretStr
    AUTH_URL: str
    TOKEN_URL: str
    METADATA_URL: str
    SCOPES: list[str] = ["openid", "email", "profile"]
