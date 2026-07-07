"""
Define an abstract base class AbstractUserService.

This class works with User.
"""

import logging
from abc import ABC, abstractmethod

from api.schemas import (
    UserCreate,
    UserDetail,
    UserLite,
    UserUpdate,
)
from api.schemas.event import EventDetail
from application.ports.repositories import ReservationServiceRepository, UserRepository
from application.services import CrudServiceBase
from core.bootstrap.exceptions import Entity
from infrastructure.openid import UserInfo

logger = logging.getLogger(__name__)


class AbstractUserService(
    CrudServiceBase[
        UserLite,
        UserDetail,
        UserRepository,
        UserCreate,
        UserUpdate,
    ],
    ABC,
):
    """
    Abstract class defines the interface for a user service.

    Provides CRUD operations for a specific UserModel.
    """

    @abstractmethod
    async def create_user(
        self,
        user_data: UserInfo,
    ) -> UserLite:
        """
        Create a User in the database.

        :param user_data: Received data from IS.

        :return: the created UserLite.
        """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserLite:
        """
        Retrieve a User instance by its username.

        :param username: The username of the UserLite.

        :return: The UserLite instance if found, None otherwise.
        """

    @abstractmethod
    async def get_events_by_user(
        self,
        user: UserLite,
        page: int = 1,
        limit: int = 20,
        past: bool | None = None,
    ) -> list[EventDetail]:
        """
        Retrieve all events linked to a given UserLite.

        :param user: The User object in database.
        :param page: The page number for pagination. Defaults to 1.
        :param limit: The maximum number of events to return per page. Defaults to 20.
        :param past: Filter for event time. `True` for past events, `False` for future events.
            `None` to fetch all events (no time filtering).

        :return: List of EventWithCalendarInfo objects linked to the user.
        """


class UserService(AbstractUserService):
    """Class UserService represent service that work with UserLite."""

    def __init__(
        self,
        user_repository: UserRepository,
        reservation_service_repository: ReservationServiceRepository,
    ):
        super().__init__(user_repository, Entity.USER)
        self.reservation_service_repo = reservation_service_repository

    async def create_user(
        self,
        user_data: UserInfo,
    ) -> UserLite:
        user = await self.get_by_username(user_data.preferred_username)
        if not user:
            logger.info(
                "User with username %s not found, creating in db.", user_data.preferred_username
            )

        user_roles = []

        services_aliases = await self.reservation_service_repo.get_all_aliases()
        for role in user_data.roles:
            if role.startswith("service_admin:"):
                service_name = role.split(":", 1)[1]
                if service_name in services_aliases:
                    user_roles.append(service_name)

        active_member = False
        for service in user_data.services:
            if service == "active":
                active_member = True

        if user:
            user_update = UserUpdate(
                provider_id=user_data.sub,
                active_member=active_member,
                roles=user_roles,
            )
            return await self.update(user.id, user_update)

        user_create = UserCreate(
            username=user_data.preferred_username,
            full_name=user_data.name,
            provider_id=user_data.sub,
            active_member=active_member,
            roles=user_roles,
        )
        return await self.repo.create(user_create)

    async def get_by_username(self, username: str) -> UserLite:
        return await self.repo.get_by_username(username)

    async def get_events_by_user(
        self,
        user: UserLite,
        page: int = 1,
        limit: int = 20,
        past: bool | None = None,
    ) -> list[EventDetail]:
        events = await self.repo.get_events_by_user_id(user.id, page, limit, past)

        return [EventDetail.model_validate(event) for event in events]
