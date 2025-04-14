"""
This module defines an abstract base class AbstractUserService that work with User
"""
from typing import Annotated
from abc import ABC, abstractmethod

from fastapi import Depends
from db import get_db
from crud import CRUDUser, CRUDReservationService
from services import CrudServiceBase
from models import UserModel
from schemas import UserCreate, UserUpdate, User, UserIS, Role, ServiceValidity
from sqlalchemy.orm import Session


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
    def create_user(
            self, user_data: UserIS,
            roles: list[Role],
            services: list[ServiceValidity]
    ) -> UserModel:
        """
        Create a User in the database.

        :param user_data: Received data from IS.
        :param roles: List of user roles in IS.
        :param services: List of user services in IS.

        :return: the created User.
        """

    @abstractmethod
    def get_by_username(self, username: str) -> UserModel:
        """
        Retrieves a User instance by its username.

        :param username: The username of the User.

        :return: The User instance if found, None otherwise.
        """


class UserService(AbstractUserService):
    """
    Class UserService represent service that work with User
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.reservation_service_crud = CRUDReservationService(db)
        super().__init__(CRUDUser(db))

    def create_user(
            self, user_data: UserIS,
            roles: list[Role],
            services: list[ServiceValidity]
    ) -> UserModel:
        user = self.get_by_username(user_data.username)

        user_roles = []

        for role in roles:
            if role.role == "service_admin":
                for manager in role.limit_objects:
                    if manager.alias in self.reservation_service_crud.get_all_aliases():
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
                active_member=active_member,
                section_head=section_head,
                roles=user_roles,
            )
            return self.update(user.id, user_update)

        user_create = UserCreate(
            id=user_data.id,
            username=user_data.username,
            active_member=active_member,
            section_head=section_head,
            roles=user_roles,
        )
        return self.crud.create(user_create)

    def get_by_username(self, username: str) -> UserModel:
        return self.crud.get_by_username(username)
