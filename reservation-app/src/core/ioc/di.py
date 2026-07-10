"""Dependency injection setup and provider registration."""

from core.ioc.providers import DatabaseProvider, RepositoryProvider
from dishka import Provider


def get_providers() -> list[Provider]:
    """
    Return a list of Dishka providers for dependency injection.

    :return: A list of configured providers.
    """
    return [
        DatabaseProvider(),
        RepositoryProvider(),
    ]
