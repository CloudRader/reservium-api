"""Module defining application-level singletons for external providers."""

from application.ports.providers.calendar import CalendarProvider
from application.ports.providers.identity import IdentityProvider
from application.services.email import EmailService
from infrastructure.google.google_calendar_services import GoogleCalendarProvider
from infrastructure.openid.openid_auth import OpenIdProvider


class Providers:
    """
    Registry for application external service providers.

    Holds singletons for calendar, identity, and email services.
    """

    def __init__(
        self,
        calendar_provider: CalendarProvider,
        identity_provider: IdentityProvider,
        email_service: EmailService,
    ):
        """
        Initialize the provider registry.

        :param calendar_provider: Google Calendar provider instance.
        :param identity_provider: OpenID identity provider instance.
        :param email_service: Email service instance.
        """
        self.calendar_provider = calendar_provider
        self.identity_provider = identity_provider
        self.email_service = email_service


def create_providers() -> Providers:
    """
    Create and return initialized provider singletons.

    :return: A Providers instance containing the active provider configurations.
    """
    return Providers(
        calendar_provider=GoogleCalendarProvider(),
        identity_provider=OpenIdProvider(),
        email_service=EmailService(),
    )
