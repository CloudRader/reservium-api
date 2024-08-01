"""
This module defines an abstract base class AbstractReservationServiceService
that work with Reservation Service
"""
from typing import Annotated
from abc import ABC, abstractmethod
from uuid import UUID

from db import get_db
from fastapi import Depends
from crud import CRUDReservationService
from services import CrudServiceBase
from models import ReservationServiceModel
from schemas import ReservationServiceCreate, ReservationServiceUpdate, User
from sqlalchemy.orm import Session


class AbstractReservationServiceService(CrudServiceBase[
                                            ReservationServiceModel,
                                            CRUDReservationService,
                                            ReservationServiceCreate,
                                            ReservationServiceUpdate,
                                        ], ABC):
    """
    This abstract class defines the interface for a reservation service ser
    that provides CRUD operations for a specific ReservationServiceModel.
    """

    @abstractmethod
    def create_reservation_service(self, reservation_service_create: ReservationServiceCreate,
                                   user: User) -> ReservationServiceModel | None:
        """
        Create a Reservation Service in the database.

        :param reservation_service_create: ReservationServiceCreate Schema for create.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the created Reservation Service.
        """

    @abstractmethod
    def update_reservation_service(self, uuid: UUID,
                                   reservation_service_update: ReservationServiceUpdate,
                                   user: User) -> ReservationServiceModel | None:
        """
        Update a Reservation Service in the database.

        :param uuid: The uuid of the Reservation Service.
        :param reservation_service_update: ReservationServiceUpdate Schema for update.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the updated Reservation Service.
        """

    @abstractmethod
    def delete_reservation_service(self, uuid: UUID,
                                   user: User) -> ReservationServiceModel | None:
        """
        Delete a Reservation Service in the database.

        :param uuid: The uuid of the Reservation Service.
        :param user: the UserSchema for control permissions of the reservation service.

        :return: the deleted Reservation Service.
        """

    @abstractmethod
    def get_by_alias(self, alias: str,
                     include_removed: bool = False) -> ReservationServiceModel | None:
        """
        Retrieves a Reservation Service instance by its alias.

        :param alias: The alias of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Services instance if found, None otherwise.
        """

    @abstractmethod
    def get_by_name(self, name: str,
                    include_removed: bool = False) -> ReservationServiceModel | None:
        """
        Retrieves a Reservation Service instance by its name.

        :param name: The name of the Reservation Service.
        :param include_removed: Include removed object or not.

        :return: The Reservation Service instance if found, None otherwise.
        """


class ReservationServiceService(AbstractReservationServiceService):
    """
    Class MiniServiceService represent service that work with Mini Service
    """

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        super().__init__(CRUDReservationService(db))

    def create_reservation_service(self, reservation_service_create: ReservationServiceCreate,
                                   user: User) -> ReservationServiceModel | None:
        if self.crud.get_by_name(reservation_service_create.name, True) or \
                self.crud.get_by_alias(reservation_service_create.alias, True):
            return None

        if not user.section_head:
            return None

        return self.crud.create(reservation_service_create)

    def update_reservation_service(self, uuid: UUID,
                                   reservation_service_update: ReservationServiceUpdate,
                                   user: User) -> ReservationServiceModel | None:
        if not user.section_head:
            return None

        return self.update(uuid, reservation_service_update)

    def delete_reservation_service(self, uuid: UUID,
                                   user: User) -> ReservationServiceModel | None:
        if not user.section_head:
            return None

        return self.crud.soft_remove(uuid)

    def get_by_alias(self, alias: str,
                     include_removed: bool = False) -> ReservationServiceModel | None:
        return self.crud.get_by_alias(alias, include_removed)

    def get_by_name(self, name: str,
                    include_removed: bool = False) -> ReservationServiceModel | None:
        return self.crud.get_by_name(name, include_removed)
