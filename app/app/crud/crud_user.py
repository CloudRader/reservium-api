"""
This module defines the CRUD operations for the User model, including an
abstract base class (AbstractCRUDUser) and a concrete implementation (CRUDUser)
using SQLAlchemy.
"""
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Type

from sqlalchemy.orm import Session

import models
import schemas

from crud import CRUDBase


class AbstractCRUDUser(CRUDBase[
                           models.User,
                           schemas.UserCreate,
                           schemas.UserUpdate
                       ], ABC):
    """
    Abstract class for CRUD operations specific to the User model.
    It extends the generic CRUDBase class and defines additional abstract methods
    for querying and manipulating User instances.
    """


class CRUDUser(AbstractCRUDUser):
    """
    Concrete class for CRUD operations specific to the User model.
    It extends the abstract AbstractCRUDDocument class and implements the required methods
    for querying and manipulating User instances.
    """

    def __init__(self, db: Session):
        super().__init__(models.User, db)
