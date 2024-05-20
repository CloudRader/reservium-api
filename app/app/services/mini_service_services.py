"""
This module defines an abstract base class AbstractMiniServiceService that work with Mini Service
"""
from typing import Annotated
from fastapi import Depends
from uuid import UUID

from db import get_db
from abc import ABC, abstractmethod
from crud import CRUDMiniService, CRUDCalendar
from services import CrudServiceBase
from models import MiniServiceModel
from schemas import MiniServiceCreate, MiniServiceUpdate, CalendarUpdate
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


class MiniServiceService(AbstractMiniServiceService):
    """
    Class MiniServiceService represent service that work with Mini Service
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.calendar_crud = CRUDCalendar(db)
        super().__init__(CRUDMiniService(db))

    def create(self, mini_service_create: MiniServiceCreate) -> MiniServiceModel | None:
        if self.crud.get_by_name(mini_service_create.name):
            return None
        return self.crud.create(mini_service_create)

    def remove(self, uuid: UUID | str | None) -> MiniServiceModel | None:
        mini_service = self.crud.get(uuid)
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
