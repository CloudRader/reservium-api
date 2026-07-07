"""Email config."""

from fastapi_mail import ConnectionConfig
from pydantic import BaseModel, SecretStr


class MailConfig(BaseModel):
    """Config for mail."""

    USERNAME: str
    PASSWORD: SecretStr
    FROM_NAME: str
    PORT: int = 587
    SERVER: str = "smtp.gmail.com"
    TLS: bool = True
    SSL: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    SENT_DORMITORY_HEAD: bool = False
    DORMITORY_HEAD_EMAIL: str = ""


# To avoid circular import of settings during module loading,
# we construct email_connection dynamically on first access.
_email_connection = None
email_connection: ConnectionConfig


def __getattr__(name: str):
    global _email_connection
    if name == "email_connection":
        if _email_connection is None:
            from core.config import settings

            _email_connection = ConnectionConfig(
                MAIL_USERNAME=settings.MAIL.USERNAME,
                MAIL_PASSWORD=settings.MAIL.PASSWORD,
                MAIL_FROM=settings.MAIL.USERNAME,
                MAIL_PORT=settings.MAIL.PORT,
                MAIL_SERVER=settings.MAIL.SERVER,
                MAIL_FROM_NAME=settings.MAIL.FROM_NAME,
                MAIL_STARTTLS=settings.MAIL.TLS,
                MAIL_SSL_TLS=settings.MAIL.SSL,
                USE_CREDENTIALS=settings.MAIL.USE_CREDENTIALS,
                VALIDATE_CERTS=settings.MAIL.VALIDATE_CERTS,
            )
        return _email_connection

    message = f"module {__name__} has no attribute {name}"
    raise AttributeError(message)
