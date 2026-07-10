"""
SMTP Mail Server configuration and connection factory.

Loads mail credentials and host settings from environment variables and
dynamically instantiates a ConnectionConfig for fastapi-mail on demand.
"""

from fastapi_mail import ConnectionConfig
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MailConfig(BaseSettings):
    """
    Configuration settings for sending transactional emails via SMTP.

    Loads and maps connection details (username, password, port, TLS/SSL preferences)
    and optional system notifications properties (dormitory head notification).
    """

    username: str = Field(validation_alias="MAIL_USERNAME")
    password: SecretStr = Field(validation_alias="MAIL_PASSWORD")
    from_name: str = Field(validation_alias="MAIL_FROM_NAME")
    port: int = Field(default=587, validation_alias="MAIL_PORT")
    server: str = Field(default="smtp.gmail.com", validation_alias="MAIL_SERVER")
    tls: bool = Field(default=True, validation_alias="MAIL_TLS")
    ssl: bool = Field(default=False, validation_alias="MAIL_SSL")
    use_credentials: bool = Field(default=True, validation_alias="MAIL_USE_CREDENTIALS")
    validate_certs: bool = Field(default=True, validation_alias="MAIL_VALIDATE_CERTS")
    sent_dormitory_head: bool = Field(default=False, validation_alias="MAIL_SENT_DORMITORY_HEAD")
    dormitory_head_email: str = Field(default="", validation_alias="MAIL_DORMITORY_HEAD_EMAIL")

    @property
    def connection(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=self.username,
            MAIL_PASSWORD=self.password,
            MAIL_FROM=self.username,
            MAIL_PORT=self.port,
            MAIL_SERVER=self.server,
            MAIL_FROM_NAME=self.from_name,
            MAIL_STARTTLS=self.tls,
            MAIL_SSL_TLS=self.ssl,
            USE_CREDENTIALS=self.use_credentials,
            VALIDATE_CERTS=self.validate_certs,
        )

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=True,
        env_file=".env",
    )
