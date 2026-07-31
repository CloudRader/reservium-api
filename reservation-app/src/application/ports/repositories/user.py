"""
Define the repository port interface for User domain entities.

This module establishes the contract for CRUD and query operations on User
entities, decoupled from database-specific implementation details.
"""

from abc import ABC, abstractmethod

from application.ports.repositories import BaseRepository
from domain.entities import User


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
