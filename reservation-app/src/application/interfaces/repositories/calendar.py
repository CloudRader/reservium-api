"""
Define CRUD operations for the Calendar model.

Includes an abstract base class (AbstractCRUDCalendar) and a concrete
implementation (CRUDCalendar) using SQLAlchemy.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from api.schemas import CalendarCreate, CalendarUpdate
from application.interfaces.repositories import BaseRepository
from domain.models import CalendarModel, MiniServiceModel


class CalendarRepository(
    BaseRepository[CalendarModel, CalendarCreate, CalendarUpdate],
    ABC,
):
    """
    Abstract class for CRUD operations specific to the Calendar model.

    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating Calendar instances.
    """

    @abstractmethod
    async def get_with_collisions(
        self,
        id_: UUID,
        include_removed: bool = False,
    ) -> CalendarModel | None:
        """
        Retrieve a single record by its id_ with collisions.

        If include_removed is True retrieve a single record
        including marked as deleted.
        """

    @abstractmethod
    async def create_with_mini_services_and_collisions(
        self,
        calendar_create: CalendarCreate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
        """
        Create a new Calendar instance with associated mini services and collisions.

        This method extends the base create method by:
        - Attaching multiple MiniServiceModel instances to the created calendar.
        - Creating symmetric collision relationships with other Calendar instances
          as specified in the input.

        :param calendar_create: Data used to create the Calendar (schema or dict).
        :param mini_services: List of MiniServiceModel objects to associate with the calendar.

        :return: The created CalendarModel instance with mini services and collisions attached.
        """

    @abstractmethod
    async def update_with_mini_services_and_collisions(
        self,
        db_obj: CalendarModel,
        obj_in: CalendarUpdate | dict[str, Any],
        mini_services: list[MiniServiceModel],
    ) -> CalendarModel:
        """
        Update an existing Calendar instance including mini services and collisions.

        This method extends the base update functionality by:
        - Replacing the existing mini services with the provided list.
        - Updating symmetric collision relationships for the calendar.
          Existing collisions are removed and replaced according to the input.

        :param db_obj: The existing CalendarModel instance to update.
        :param obj_in: Data to update the Calendar (schema or dict).
        :param mini_services: List of MiniServiceModel objects to associate with the calendar.

        :return: The updated CalendarModel instance with updated mini services and collisions.
        """

    @abstractmethod
    async def get_by_reservation_type(
        self,
        reservation_type: str,
        include_removed: bool = False,
    ) -> CalendarModel | None:
        """
        Retrieve a Calendar instance by its reservation type.

        :param reservation_type: The reservation type of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """

    @abstractmethod
    async def get_by_provider_id(
        self,
        provider_id: str,
        include_removed: bool = False,
    ) -> CalendarModel | None:
        """
        Retrieve a Calendar instance by its provider ID.

        :param provider_id: The provider ID of the Calendar.
        :param include_removed: Include removed object or not.

        :return: The Calendar instance if found, None otherwise.
        """
