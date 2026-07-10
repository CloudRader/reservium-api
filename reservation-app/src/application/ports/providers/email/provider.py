"""Defines a interface port for working with the Email Provider."""

from abc import ABC, abstractmethod
from typing import Any

from fastapi import BackgroundTasks
from infrastructure.email.schemas import EmailCreate, RegistrationFormCreate


class EmailProvider(ABC):
    """Interface for a service interacting with the Email Provider."""

    @abstractmethod
    def prepare_registration_form(
        self,
        registration_form: RegistrationFormCreate,
        full_name: str,
    ) -> EmailCreate:
        """
        Prepare registration form in pdf for sending to head of the dormitory.

        :param registration_form: Input data for adding in pdf.
        :param full_name: User fullname.

        :returns EmailCreate json object: the created event or exception otherwise.
        """

    @abstractmethod
    async def send_email(
        self,
        email_create: EmailCreate,
        background_tasks: BackgroundTasks,
    ) -> Any:
        """
        Send an email asynchronously.

        :param email_create: Email Create schema.
        :param background_tasks: BackgroundTasks used to run the email sending asynchronously.

        :returns Any: Response indicating status of the sent email.
        """
