"""
Define an abstract base class AbstractUserService.

This class works with User.
"""

import logging
from abc import ABC, abstractmethod
from typing import Annotated

from core import db_session
from core.application.exceptions import Entity, EntityNotFoundError
from core.schemas import (
    UserCreate,
    UserDetail,
    UserKeycloak,
    UserLite,
    UserUpdate,
)
from core.schemas.event import EventDetail, EventTimeline
from crud import CRUDReservationService, CRUDUser
from fastapi import Depends
from services import CrudServiceBase, EventService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


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
        user_data: UserKeycloak,
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

    @abstractmethod
    async def get_events_by_user_filter_past_and_upcoming(
        self, user: UserLite
    ) -> list[EventDetail]:
        """
        Retrieve all events linked to the given user and split them into past and upcoming.

        :param user: The User object in database.

        :return: EventTimeline object containing two lists:
             - ``past``: events that have already ended,
             - ``upcoming``: events scheduled for the future.
        """


class UserService(AbstractUserService):
    """Class UserService represent service that work with UserLite."""

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(db_session.scoped_session_dependency)],
    ):
        super().__init__(CRUDUser(db), Entity.USER)
        self.reservation_service_crud = CRUDReservationService(db)
        self.event_service = EventService(db)

    async def create_user(
        self,
        user_data: UserKeycloak,
    ) -> UserLite:
        try:
            user = await self.get(user_data.ldap_id)
        except EntityNotFoundError:
            user = None
            logger.info("User with LDAP ID %s not found, creating in db.", user_data.ldap_id)

        user_roles = []

        services_aliases = await self.reservation_service_crud.get_all_aliases()
        for role in user_data.roles:
            if role.startswith("service_admin:"):
                service_name = role.split(":", 1)[1]
                if service_name in services_aliases:
                    user_roles.append(service_name)

        active_member = False
        for service in user_data.services:
            if service == "active":
                active_member = True

        section_head = False
        if "superuser" in user_data.roles:
            active_member = True
            section_head = True

        if user:
            user_update = UserUpdate(
                active_member=active_member,
                section_head=section_head,
                roles=user_roles,
            )
            return await self.update(user.id, user_update)

        user_create = UserCreate(
            id=user_data.ldap_id,
            username=user_data.preferred_username,
            full_name=user_data.name,
            active_member=active_member,
            section_head=section_head,
            roles=user_roles,
        )
        return await self.crud.create(user_create)

    async def get_by_username(self, username: str) -> UserLite:
        return await self.crud.get_by_username(username)

    async def get_events_by_user(
        self,
        user: UserLite,
        page: int = 1,
        limit: int = 20,
        past: bool | None = None,
    ) -> list[EventDetail]:
        return await self.crud.get_events_by_user_id(user.id, page, limit, past)

    async def get_events_by_user_filter_past_and_upcoming(self, user: UserLite) -> EventTimeline:
        return await self.crud.get_events_by_user_filter_past_and_upcoming(user.id)
