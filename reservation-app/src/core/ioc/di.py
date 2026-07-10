"""Dependency injection setup and provider registration."""

from core.ioc.providers import (
    DatabaseProvider,
    ExternalProvidersProvider,
    RepositoryProvider,
    ServiceProvider,
    SettingsProvider,
)
from dishka import Provider


def get_providers() -> list[Provider]:
    """
    Return a list of Dishka providers for dependency injection.

    :return: A list of configured providers.
    """
    return [
        SettingsProvider(),
        DatabaseProvider(),
        ExternalProvidersProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    ]
