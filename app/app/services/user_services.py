"""
This module defines an abstract base class AbstractUserService that work with User
"""
from typing import Annotated
from abc import ABC, abstractmethod

from fastapi import Depends
from db import db_session
from crud import CRUDUser, CRUDReservationService
from services import CrudServiceBase
from models import UserModel
from schemas import UserCreate, UserUpdate, User, UserIS, Role, ServiceValidity, \
    Room
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractUserService(CrudServiceBase[
                              User,
                              CRUDUser,
                              UserCreate,
                              UserUpdate,
                          ], ABC):
    """
    This abstract class defines the interface for a user service
    that provides CRUD operations for a specific UserModel.
    """

    @abstractmethod
    async def create_user(
            self, user_data: UserIS,
            roles: list[Role],
            services: list[ServiceValidity],
            room: Room
    ) -> UserModel:
        """
        Create a User in the database.

        :param user_data: Received data from IS.
        :param roles: List of user roles in IS.
        :param services: List of user services in IS.
        :param room: Room of user in IS.

        :return: the created User.
        """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserModel:
        """
        Retrieves a User instance by its username.

        :param username: The username of the User.

        :return: The User instance if found, None otherwise.
        """


class UserService(AbstractUserService):
    """
    Class UserService represent service that work with User
    """

    def __init__(self, db: Annotated[
        AsyncSession, Depends(db_session.scoped_session_dependency)]):
        self.reservation_service_crud = CRUDReservationService(db)
        super().__init__(CRUDUser(db))

    async def create_user(
            self, user_data: UserIS,
            roles: list[Role],
            services: list[ServiceValidity],
            room: Room
    ) -> UserModel:
        user = await self.get_by_username(user_data.username)

        user_roles = []

        for role in roles:
            if role.role == "service_admin":
                for manager in role.limit_objects:
                    if manager.alias in await self.reservation_service_crud.get_all_aliases():
                        user_roles.append(manager.alias)

        active_member = False
        for service in services:
            if service.service.alias == "active":
                active_member = True

        section_head = False
        if user_data.note.strip() == "head":
            active_member = True
            section_head = True

        if user:
            user_update = UserUpdate(
                room_number=room.door_number,
                active_member=active_member,
                section_head=section_head,
                roles=user_roles,
            )
            return await self.update(user.id, user_update)

        user_create = UserCreate(
            id=user_data.id,
            username=user_data.username,
            full_name=f"{user_data.first_name} {user_data.surname}",
            room_number=room.door_number,
            active_member=active_member,
            section_head=section_head,
            roles=user_roles,
        )
        return await self.crud.create(user_create)

    async def get_by_username(self, username: str) -> UserModel:
        return await self.crud.get_by_username(username)
