"""
This module defines an abstract base class AbstractAccessCardSystem
that work with Access Card System.
"""
from typing import Annotated
from abc import ABC, abstractmethod

from fastapi import Depends
from db import db_session
from api import PermissionDeniedException
from services import EventService
from schemas import VarSymbolCreateUpdate, VarSymbolDelete, ClubAccessSystemRequest
from crud import CRUDEvent, CRUDUser, CRUDReservationService, CRUDMiniService
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractAccessCardSystemService(ABC):
    """
    This abstract class defines the interface for an email service.
    """

    @abstractmethod
    async def add_var_symbol(
            self,
            access_body: VarSymbolCreateUpdate
    ) -> dict:
        """
        Add or update a variable symbol in the access group.

        :param access_body: Body for create or update var symbol in ACS.

        :returns: The body fot the API.
        """

    @abstractmethod
    async def del_var_symbol(
            self,
            access_body: VarSymbolDelete,
    ) -> dict:
        """
        Delete a variable symbol from the access group.

        :param access_body: Body for delete var symbol in ACS.

        :returns: The result from the API.
        """

    @abstractmethod
    async def get_groups_for_use(self):
        """
        Get the list of available groups for the API key.

       :returns: The body fot the API.
        """

    @abstractmethod
    async def get_access_var_symbol(
            self,
            var_symbol: str,
    ) -> dict:
        """
        Get the list of groups for a given variable symbol.

        :param var_symbol: The var symbol that identifies the user in ISKAM.

        :returns: The body fot the API.
        """

    @abstractmethod
    async def get_access_group(
            self,
            group: str,
    ) -> dict:
        """
        Get the list of variable symbols for a given group.

        :param group: The group of the reader in the ACS.

        :returns: The body fot the API.
        """

    @abstractmethod
    async def reservation_access_authorize(
            self,
            service_event: Annotated[EventService, Depends(EventService)],
            access_request: ClubAccessSystemRequest
    ) -> bool:
        """
        Perform access control check for a reservation based on UID user, room, and device.

        :param service_event: Event service.
        :param access_request: Request containing UID, room_id, and device_id.

        :returns: True if access is authorized, False otherwise.
        """


class AccessCardSystemService(AbstractAccessCardSystemService):
    """
    Class AccessCardSystemService represent service that work with Access Card System.
    """

    def __init__(self, db: Annotated[
        AsyncSession, Depends(db_session.scoped_session_dependency)]):
        self.event_crud = CRUDEvent(db)
        self.user_crud = CRUDUser(db)
        self.reservation_service_crud = CRUDReservationService(db)
        self.mini_service_crud = CRUDMiniService(db)

    async def reservation_access_authorize(
            self,
            service_event: Annotated[EventService, Depends(EventService)],
            access_request: ClubAccessSystemRequest
    ) -> bool:
        user = await self.user_crud.get(access_request.uid)

        if user is None:
            raise PermissionDeniedException("This user isn't exist in system.")

        reservation_service = await self.reservation_service_crud.get_by_room_id(
            access_request.room_id)
        mini_service = await self.mini_service_crud.get_by_room_id(access_request.room_id)

        if (reservation_service is None) and (mini_service is None):
            raise PermissionDeniedException("This room associated with some service isn't exist "
                                            "in system or use another access system")

        event = await service_event.get_current_event_for_user(user.id)

        if event is None:
            raise PermissionDeniedException("No available reservation exists at this time.")

        if mini_service and (mini_service.name in event.additional_services):
            if access_request.device_id in mini_service.lockers_id:
                return True

        if reservation_service == await service_event.get_reservation_service_of_this_event(event):
            if access_request.device_id in reservation_service.lockers_id:
                return True

            for mini_service_name in event.additional_services:
                mini_service = await self.mini_service_crud.get_by_name(mini_service_name)
                if (mini_service.room_id is None) and (access_request.device_id in
                                                       mini_service.lockers_id):
                    return True

        raise PermissionDeniedException("No matching reservation exists at this time "
                                        "for this rules.")

    async def add_var_symbol(
            self,
            access_body: VarSymbolCreateUpdate
    ) -> dict:
        data = {
            "funkce": "AddVarSymbolSkupina",
            "varsymbol": access_body.var_symbol,
            "skupina": access_body.group,
            "platnostod": access_body.valid_from,
            "platnostdo": access_body.valid_to
        }
        return data

    async def del_var_symbol(
            self,
            access_body: VarSymbolDelete,
    ) -> dict:
        data = {
            "funkce": "DelVarSymbolSkupina",
            "varsymbol": access_body.var_symbol,
            "skupina": access_body.group
        }
        return data

    async def get_groups_for_use(self):
        data = {
            "funkce": "GetSkupinyForUse",
        }
        return data

    async def get_access_var_symbol(
            self,
            var_symbol: str,
    ) -> dict:
        data = {
            "funkce": "GetPristupVarSymbol",
            "varsymbol": var_symbol
        }
        return data

    async def get_access_group(
            self,
            group: str,
    ) -> dict:
        data = {
            "funkce": "GetPristupSkupina",
            "skupina": group
        }
        return data
