"""
Define an abstract base class AbstractUserService.

This class works with UserLite.
"""

from abc import ABC, abstractmethod
from typing import Annotated

from core import db_session
from core.schemas import (
    Role,
    Room,
    ServiceValidity,
    UserCreate,
    UserDetail,
    UserIS,
    UserLite,
    UserUpdate,
)
from core.schemas.event import EventDetail
from crud import CRUDReservationService, CRUDUser
from fastapi import Depends
from services import CrudServiceBase, EventService
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractUserService(
    CrudServiceBase[
        UserLite,
        UserDetail,
        CRUDUser,
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
        user_data: UserIS,
        roles: list[Role],
        services: list[ServiceValidity],
        room: Room,
    ) -> UserLite:
        """
        Create a UserLite in the database.

        :param user_data: Received data from IS.
        :param roles: List of user roles in IS.
        :param services: List of user services in IS.
        :param room: Room of user in IS.

        :return: the created UserLite.
        """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserLite:
        """
        Retrieve a UserLite instance by its username.

        :param username: The username of the UserLite.

        :return: The UserLite instance if found, None otherwise.
        """

    @abstractmethod
    async def get_events_by_user(self, user: UserLite) -> list[EventDetail]:
        """
        Retrieve all events linked to a given UserLite.

        :param user: The UserLite object in database.

        :return: List of EventWithCalendarInfo objects linked to the user.
        """


class UserService(AbstractUserService):
    """Class UserService represent service that work with UserLite."""

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(db_session.scoped_session_dependency)],
    ):
        self.reservation_service_crud = CRUDReservationService(db)
        self.event_service = EventService(db)
        super().__init__(CRUDUser(db))

    async def create_user(
        self,
        user_data: UserIS,
        roles: list[Role],
        services: list[ServiceValidity],
        room: Room,
    ) -> UserLite:
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

    async def get_by_username(self, username: str) -> UserLite:
        return await self.crud.get_by_username(username)

    async def get_events_by_user(self, user: UserLite) -> list[EventDetail]:
        return await self.crud.get_events_by_user_id(user.id)
