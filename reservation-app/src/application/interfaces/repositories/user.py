"""
Define CRUD operations for the User model.

Includes an abstract base class (AbstractCRUDUser) and a concrete
implementation (CRUDUser) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from api.schemas import UserCreate, UserUpdate
from application.interfaces.repositories import BaseRepository
from domain.models import EventModel, UserModel


class UserRepository(BaseRepository[UserModel, UserCreate, UserUpdate], ABC):
    """
    Abstract class for CRUD operations specific to the User model.

    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating User instances.
    """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserModel | None:
        """
        Retrieve a User instance by its username.

        :param username: The username of the User.

        :return: The User instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_provider_id(self, provider_id: str) -> UserModel | None:
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
    ) -> list[EventModel]:
        """
        Fetch related events for a specific user with pagination and time filtering.

        :param id_: ID of the User.
        :param page: The page number for pagination. Defaults to 1.
        :param limit: The maximum number of events to return per page. Defaults to 20.
        :param past: Filter for event time. `True` for past events, `False` for future events.
            `None` to fetch all events (no time filtering).

        :return: List of related events of type `model`.
        """
