"""
Define an abstract base class AbstractAccessCardSystem.

This class works with the Access Card System.
"""

from abc import ABC, abstractmethod
from typing import Annotated

from api.schemas import ClubAccessSystemRequest
from application.services import EventService
from core.bootstrap.exceptions import PermissionDeniedError
from fastapi import Depends
from infrastructure.database import AsyncSessionDep
from infrastructure.database.sqlalchemy.repositories import (
    SQLAlchemyEventRepository,
    SQLAlchemyMiniServiceRepository,
    SQLAlchemyReservationServiceRepository,
    SQLAlchemyUserRepository,
)


class AbstractAccessCardSystemService(ABC):
    """Abstract class defines the interface for an access card system service."""

    @abstractmethod
    async def reservation_access_authorize(
        self,
        service_event: Annotated[EventService, Depends(EventService)],
        access_request: ClubAccessSystemRequest,
    ) -> bool:
        """
        Perform access control check for a reservation based on UID user, room, and device.

        :param service_event: Event service.
        :param access_request: Request containing UID, room_id, and device_id.

        :returns: True if access is authorized, False otherwise.
        """


class AccessCardSystemService(AbstractAccessCardSystemService):
    """Class AccessCardSystemService represent service that work with Access Card System."""

    def __init__(
        self,
        db: AsyncSessionDep,
    ):
        self.event_crud = SQLAlchemyEventRepository(db)
        self.user_crud = SQLAlchemyUserRepository(db)
        self.reservation_service_crud = SQLAlchemyReservationServiceRepository(db)
        self.mini_service_crud = SQLAlchemyMiniServiceRepository(db)

    async def reservation_access_authorize(
        self,
        service_event: Annotated[EventService, Depends(EventService)],
        access_request: ClubAccessSystemRequest,
    ) -> bool:
        user = await self.user_crud.get(access_request.uid)

        if user is None:
            message = "This user isn't exist in system."
            raise PermissionDeniedError(message)

        reservation_service = await self.reservation_service_crud.get_by_room_id(
            access_request.room_id,
        )
        mini_service = await self.mini_service_crud.get_by_room_id(
            access_request.room_id,
        )

        if (reservation_service is None) and (mini_service is None):
            message = (
                "This room associated with some service isn't exist "
                "in system or use another access system"
            )
            raise PermissionDeniedError(message)

        event = await service_event.get_current_event_for_user(user.id)

        if event is None:
            message = "No available reservation exists at this time."
            raise PermissionDeniedError(message)

        if (
            mini_service
            and mini_service.name in event.additional_services
            and access_request.device_id in mini_service.lockers_id
        ):
            return True

        if reservation_service == await service_event.get_reservation_service_of_this_event(event):
            if reservation_service and access_request.device_id in reservation_service.lockers_id:
                return True

            for mini_service_name in event.additional_services:
                mini_service = await self.mini_service_crud.get_by_name(
                    mini_service_name,
                )
                if mini_service and access_request.device_id in mini_service.lockers_id:
                    return True

        message = "No matching reservation exists at this time for this rules."
        raise PermissionDeniedError(message)
