"""
This module defines an abstract base class AbstractUserService that work with User
"""
from typing import Annotated, Type
from fastapi import Depends
from db import get_db
from abc import ABC, abstractmethod
from crud import CRUDUser
from services import CrudServiceBase
from models import User
from schemas import UserCreate, UserUpdate
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
    def get_by_username(self, username: str) -> list[Type[User]]:
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
        super().__init__(CRUDUser(db))

    def get_by_username(self, username: str) -> User:
        return self.crud.get_by_username(username)
