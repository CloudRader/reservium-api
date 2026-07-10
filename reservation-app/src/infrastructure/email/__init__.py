"""FastMail-specific service email integrations."""

from infrastructure.email.provider import FastEmailProvider
from infrastructure.email.schemas import EmailCreate, EmailMeta, RegistrationFormCreate

__all__ = [
    "EmailCreate",
    "EmailMeta",
    "FastEmailProvider",
    "RegistrationFormCreate",
]
