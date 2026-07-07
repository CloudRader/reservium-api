"""Google API configuration."""

from pydantic import BaseModel, SecretStr


class GoogleConfig(BaseModel):
    """Config for google."""

    TYPE: str = "service_account"
    PROJECT_ID: str
    PRIVATE_KEY_ID: SecretStr
    PRIVATE_KEY: SecretStr
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
            "private_key_id": self.PRIVATE_KEY_ID.get_secret_value(),
            "private_key": self.PRIVATE_KEY.get_secret_value().replace("\\n", "\n"),
            "client_email": self.CLIENT_EMAIL,
            "client_id": self.CLIENT_ID,
            "auth_uri": self.AUTH_URI,
            "token_uri": self.TOKEN_URI,
            "auth_provider_x509_cert_url": self.AUTH_PROVIDER_X509_CERT_URL,
            "client_x509_cert_url": self.CLIENT_X509_CERT_URL,
        }
