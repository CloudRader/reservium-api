"""
Define the repository port interface for User domain entities.

This module establishes the contract for CRUD and query operations on User
entities, decoupled from database-specific implementation details.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from application.ports.repositories import BaseRepository
from domain.entities import Event, User


class UserRepository(BaseRepository[User], ABC):
    """
    Repository port interface for User domain entities.

    Establishes abstract operations specific to Users, extending the base
    repository interface.
    """

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a User instance by its username.

        :param username: The username of the User.

        :return: The User instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_provider_id(self, provider_id: str) -> User | None:
        """
        Retrieve a User instance by its provider_id.

        :param provider_id: The provider ID of the User.

        :return: The User instance if found, None otherwise.
        """

    @abstractmethod
    async def get_events_by_user_id(
        self,
        id_: UUID,
        page: int = 1,
        limit: int = 20,
        past: bool | None = None,
    ) -> list[Event]:
        """
        Fetch related events for a specific user with pagination and time filtering.

        :param id_: ID of the User.
        :param page: The page number for pagination. Defaults to 1.
        :param limit: The maximum number of events to return per page. Defaults to 20.
        :param past: Filter for event time. `True` for past events, `False` for future events.
            `None` to fetch all events (no time filtering).

        :return: List of related events.
        """
