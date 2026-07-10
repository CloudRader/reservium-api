"""
Google Workspace API and Calendar integration settings.

Loads and validates Google Service Account credentials and scopes from
environment variables prefixed with `GOOGLE_`.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleConfig(BaseSettings):
    """
    Configuration settings for Google API integrations.

    Loads and validates Google Service Account credentials and scopes from
    environment variables prefixed with `GOOGLE_`. Provides a helper property
    to format the credentials for the Google API client library.
    """

    type: str = Field(default="service_account", validation_alias="GOOGLE_TYPE")
    project_id: str = Field(validation_alias="GOOGLE_PROJECT_ID")
    private_key_id: SecretStr = Field(validation_alias="GOOGLE_PRIVATE_KEY_ID")
    private_key: SecretStr = Field(validation_alias="GOOGLE_PRIVATE_KEY")
    client_email: str = Field(validation_alias="GOOGLE_CLIENT_EMAIL")
    client_id: str = Field(validation_alias="GOOGLE_CLIENT_ID")
    auth_uri: str = Field(
        default="https://accounts.google.com/o/oauth2/auth", validation_alias="GOOGLE_AUTH_URI"
    )
    token_uri: str = Field(
        default="https://oauth2.googleapis.com/token", validation_alias="GOOGLE_TOKEN_URI"
    )
    auth_provider_x509_cert_url: str = Field(
        default="https://www.googleapis.com/oauth2/v1/certs",
        validation_alias="GOOGLE_AUTH_PROVIDER_X509_CERT_URL",
    )
    client_x509_cert_url: str = Field(validation_alias="GOOGLE_CLIENT_X509_CERT_URL")
    scopes: list[str] = Field(
        default=["https://www.googleapis.com/auth/calendar"], validation_alias="GOOGLE_SCOPES"
    )

    @property
    def info(self) -> dict:
        """Return service account credentials in Google-compatible format."""
        return {
            "type": self.type,
            "project_id": self.project_id,
            "private_key_id": self.private_key_id.get_secret_value(),
            "private_key": self.private_key.get_secret_value().replace("\\n", "\n"),
            "client_email": self.client_email,
            "client_id": self.client_id,
            "auth_uri": self.auth_uri,
            "token_uri": self.token_uri,
            "auth_provider_x509_cert_url": self.auth_provider_x509_cert_url,
            "client_x509_cert_url": self.client_x509_cert_url,
        }

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=True,
        env_file=".env",
    )
