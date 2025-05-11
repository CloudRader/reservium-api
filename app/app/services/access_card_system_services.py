"""
This module defines an abstract base class AbstractAccessCardSystem
that work with Access Card System.
"""
from typing import Annotated
from abc import ABC, abstractmethod

from fastapi import Depends
from db import db_session
from schemas import VarSymbolCreateUpdate, VarSymbolDelete
from crud import CRUDEvent
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


class AccessCardSystemService(AbstractAccessCardSystemService):
    """
    Class AccessCardSystemService represent service that work with Access Card System.
    """

    def __init__(self, db: Annotated[
        AsyncSession, Depends(db_session.scoped_session_dependency)]):
        self.event_crud = CRUDEvent(db)

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
