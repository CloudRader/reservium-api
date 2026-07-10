"""Defines a interface port for working with the Email Provider."""

from abc import ABC, abstractmethod

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
