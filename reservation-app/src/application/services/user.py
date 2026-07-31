"""
Define user application services.

This module provides abstract and concrete user application services for managing
User domain entities, user role assignments, and Identity Provider user synchronization.
"""

import logging
from abc import ABC, abstractmethod

from application.mappers import UserMapper
from application.ports.repositories import (
    ReservationServiceRepository,
    UserRepository,
)
from application.schemas import (
    UserCreate,
    UserSchema,
    UserUpdate,
)
from application.services import BaseService
from core.bootstrap.exceptions import Entity, EntityNotFoundError
from domain.entities import User
from infrastructure.identity.openid.schemas import UserInfo

logger = logging.getLogger(__name__)


class AbstractUserService(
    BaseService[
        UserSchema,
        UserRepository,
        User,
        UserCreate,
        UserUpdate,
    ],
    ABC,
):
    """
    Abstract class defining the contract for user application services.

    Provides operations for managing User domain entities and synchronizing identity data.
    """

    @abstractmethod
    async def create_user(
        self,
        user_data: UserInfo,
    ) -> UserSchema:
        """
        Create or update a User domain entity from Identity Provider UserInfo data.

        :param user_data: User claims received from Identity Provider.
        :return: Lite DTO representation of the created or updated user entity.
        """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserSchema:
        """
        Retrieve a User domain entity by its username and map to a UserLite DTO.

        :param username: The username of the User.
        :return: Lite DTO representation if found, None otherwise.
        """


class UserService(AbstractUserService):
    """Application service implementing user management and identity synchronization."""

    def __init__(
        self,
        user_repository: UserRepository,
        reservation_service_repository: ReservationServiceRepository,
        mapper: UserMapper,
    ):
        super().__init__(
            user_repository,
            Entity.USER,
            UserSchema,
            mapper,
        )
        self.reservation_service_repo = reservation_service_repository

    async def create_user(
        self,
        user_data: UserInfo,
    ) -> UserSchema:
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
            updated_user = await self.update(user.id, user_update)
            return self.mapper.to_schema(updated_user)

        user_create = UserCreate(
            username=user_data.preferred_username,
            full_name=user_data.name,
            provider_id=user_data.sub,
            active_member=active_member,
            roles=user_roles,
        )
        new_user = await self.create(user_create)
        return self.mapper.to_schema(new_user)

    async def get_by_username(self, username: str) -> UserSchema | None:
        user = await self.repo.get_by_username(username)
        if user is None:
            raise EntityNotFoundError(self.entity_name, username)
        return self.mapper.to_schema(user)
