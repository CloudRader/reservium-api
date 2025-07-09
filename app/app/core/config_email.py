"""Email config."""

from fastapi_mail import ConnectionConfig
from core import settings

email_connection = ConnectionConfig(
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
