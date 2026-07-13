"""Defines a interface port for working with the Email Provider."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from fastapi import BackgroundTasks

if TYPE_CHECKING:
    from application.schemas.event import EventDetail
    from infrastructure.email.schemas import EmailCreate, EmailMeta, RegistrationFormCreate


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

        This endpoint sends an email using the provided email details. The email is
        sent in the background to avoid blocking the request-response cycle.

        :param email_create: Email Create schema.
        :param background_tasks: BackgroundTasks used to run the email sending asynchronously.

        :returns Dictionary: Confirming that the email has been sent.
        """

    @abstractmethod
    async def preparing_email(
        self,
        event: EventDetail,
        email_meta: EmailMeta,
        background_tasks: BackgroundTasks,
    ) -> Any:
        """
        Prepare and send both member and manager information emails based on an event.

        :param event: The EventExtra object in db.
        :param email_meta: Email metadata containing template name, subject and reason.
        :param background_tasks: BackgroundTasks used to run the email sending asynchronously.

        :return: Dictionary confirming the emails have been sent.
        """

    @abstractmethod
    def create_email_meta(self, template_name: str, subject: str, reason: str = "") -> EmailMeta:
        """
        Construct an EmailMeta object from parameters.

        :param template_name: Name of the email template.
        :param subject: Email subject.
        :param reason: Optional reason content.

        :return: EmailMeta instance.
        """
