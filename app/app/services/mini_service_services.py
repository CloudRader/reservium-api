"""
This module defines an abstract base class AbstractMiniServiceService that work with Mini Service
"""
from typing import Annotated, Type
from abc import ABC, abstractmethod
from uuid import UUID

from db import get_db
from fastapi import Depends
from crud import CRUDMiniService, CRUDCalendar
from services import CrudServiceBase
from models import MiniServiceModel
from schemas import MiniServiceCreate, MiniServiceUpdate, CalendarUpdate, User
from sqlalchemy.orm import Session


class AbstractMiniServiceService(CrudServiceBase[
                                     MiniServiceModel,
                                     CRUDMiniService,
                                     MiniServiceCreate,
                                     MiniServiceUpdate,
                                 ], ABC):
    """
    This abstract class defines the interface for a mini service ser
    that provides CRUD operations for a specific MiniServiceModel.
    """

    @abstractmethod
    def create_mini_service(self, mini_service_create: MiniServiceCreate,
                            user: User) -> MiniServiceModel | None:
        """
        Create a Mini Service in the database.

        :param mini_service_create: MiniServiceCreate Schema for create.
        :param user: the UserSchema for control permissions of the mini service.

        :return: the created Mini Service.
        """

    @abstractmethod
    def update_mini_service(self, uuid: UUID,
                            mini_service_update: MiniServiceUpdate,
                            user: User) -> MiniServiceModel | None:
        """
        Update a Mini Service in the database.

        :param uuid: The uuid of the Mini Service.
        :param mini_service_update: MiniServiceUpdate Schema for update.
        :param user: the UserSchema for control permissions of the mini service.

        :return: the updated Mini Service.
        """

    @abstractmethod
    def delete_mini_service(self, uuid: UUID,
                            user: User) -> MiniServiceModel | None:
        """
        Delete a Mini Service in the database.

        :param uuid: The uuid of the Mini Service.
        :param user: the UserSchema for control permissions of the mini service.

        :return: the deleted Mini Service.
        """

    @abstractmethod
    def get_by_service_alias(self, service_alias: str) -> list[Type[MiniServiceModel]] | None:
        """
        Retrieves a Mini Service instance by its service_alias.

        :param service_alias: The service alias of the Mini Service.

        :return: The Mini Services instance if found, None otherwise.
        """

    @abstractmethod
    def get_by_name(self, name: str) -> MiniServiceModel | None:
        """
        Retrieves a Calendar instance by its name.

        :param name: The name of the Mini Service.

        :return: The Mini Service instance if found, None otherwise.
        """


class MiniServiceService(AbstractMiniServiceService):
    """
    Class MiniServiceService represent service that work with Mini Service
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.calendar_crud = CRUDCalendar(db)
        super().__init__(CRUDMiniService(db))

    def create_mini_service(self, mini_service_create: MiniServiceCreate,
                            user: User) -> MiniServiceModel | None:
        if self.crud.get_by_name(mini_service_create.name):
            return None

        if user is None or mini_service_create.service_alias not in user.roles:
            return None

        return self.crud.create(mini_service_create)

    def update_mini_service(self, uuid: UUID,
                            mini_service_update: MiniServiceUpdate,
                            user: User) -> MiniServiceModel | None:
        mini_service_to_update = self.get(uuid)

        if user is None or mini_service_to_update.service_alias not in user.roles:
            return None

        return self.update(uuid, mini_service_update)

    def delete_mini_service(self, uuid: UUID,
                            user: User) -> MiniServiceModel | None:
        mini_service = self.crud.get(uuid)

        if user is None or mini_service.service_alias not in user.roles:
            return None

        calendars = self.calendar_crud.get_by_service_alias(mini_service.service_alias)

        for calendar in calendars:
            if mini_service.name in calendar.mini_services:
                list_of_mini_services = calendar.mini_services.copy()
                list_of_mini_services.remove(mini_service.name)
                update_exist_calendar = CalendarUpdate(
                    mini_services=list_of_mini_services
                )
                self.calendar_crud.update(db_obj=calendar, obj_in=update_exist_calendar)

        return self.crud.remove(uuid)

    def get_by_service_alias(self, service_alias: str) -> list[Type[MiniServiceModel]] | None:
        mini_services = self.crud.get_by_service_alias(service_alias)
        if len(mini_services) == 0:
            return None
        return mini_services

    def get_by_name(self, name: str) -> MiniServiceModel | None:
        return self.crud.get_by_name(name)
