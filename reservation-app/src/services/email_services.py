"""
Define an abstract base class AbstractEmailService.

This class works with Email.
"""

import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from anyio import Path as AsyncPath
from core import email_connection, settings
from core.schemas import (
    CalendarLite,
    EmailCreate,
    EmailMeta,
    EventDetail,
    EventLite,
    RegistrationFormCreate,
    ReservationServiceLite,
    UserLite,
)
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, MessageType, NameEmail
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pypdf import PdfReader, PdfWriter


class AbstractEmailService(ABC):
    """Abstract class defines the interface for an email service."""

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

        :returns EventExtra json object: the created event or exception otherwise.
        """


class EmailService(AbstractEmailService):
    """Class EmailService represent service that work with Email."""

    def __init__(
        self,
    ):
        self.template_dir = Path(__file__).parent.parent / "templates" / "email"
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir), autoescape=select_autoescape()
        )

    def prepare_registration_form(
        self,
        registration_form: RegistrationFormCreate,
        full_name: str,
    ) -> EmailCreate:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        original_pdf_path = os.path.join(
            base_dir,
            "..",
            "templates",
            "event_registration.pdf",
        )
        output_path = "/tmp/event_registration.pdf"

        # Make a copy of the original PDF
        shutil.copy(original_pdf_path, output_path)

        # Open the copied PDF and fill form fields
        reader = PdfReader(output_path)
        writer = PdfWriter()

        # Fill the fields
        writer.append(reader)

        formatted_start_date = registration_form.event_start.strftime("%H:%M, %d/%m/%Y")
        formatted_end_date = registration_form.event_end.strftime("%H:%M, %d/%m/%Y")

        writer.update_page_form_field_values(
            writer.pages[0],  # Targeting the first page
            {
                "purpose": registration_form.event_name,
                "guests": str(registration_form.guests),
                "start_date": formatted_start_date,
                "end_date": formatted_end_date,
                "full_name": full_name,
                "email": str(registration_form.email),
                "organizers": registration_form.organizers,
                "space": registration_form.space,
                "other_spaces": ", ".join(registration_form.other_space or []),
                "today_date": datetime.today().strftime("%d/%m/%Y"),
            },
        )

        # Save the filled PDF
        with open(output_path, "wb") as output_pdf:
            writer.write(output_pdf)

        emails = [registration_form.email, registration_form.manager_contact_mail]

        if settings.MAIL.SENT_DORMITORY_HEAD:
            emails.append(settings.MAIL.DORMITORY_HEAD_EMAIL)

        return EmailCreate(
            email=emails,
            subject="Event Registration Form for Approval",
            body=(
                f"Request to reserve an event for a member {full_name}.\n\n"
                "If you reserve less than 5 days in advance, your reservation may not be reviewed. "
                "Please take note of this.\n\n"
                "If your reservation is approved by the head of the dormitory "
                "(you will receive a reply to this email), "
                "please go to the reception to sign the reservation form. "
                "If you do not do so, your reservation will not be valid.\n\n"
                "With appreciation,\n"
                f"Your {settings.ORGANIZATION_NAME} Team"
            ),
            attachment=output_path,
        )

    async def send_email(self, email_create: EmailCreate, background_tasks: BackgroundTasks) -> Any:
        """
        Send an email asynchronously.

        This endpoint sends an email using the provided email details. The email is
        sent in the background to avoid blocking the request-response cycle.

        :param email_create: Email Create schema.
        :param background_tasks: BackgroundTasks used to run the email sending asynchronously.

        :returns Dictionary: Confirming that the email has been sent.
        """
        message = MessageSchema(
            subject=email_create.subject,
            recipients=[NameEmail(name=e, email=e) for e in email_create.email],
            body=email_create.body,
            subtype=MessageType.plain,
            attachments=[email_create.attachment] if email_create.attachment else [],
        )

        fm = FastMail(email_connection)

        background_tasks.add_task(
            self._send_and_cleanup,
            fm,
            message,
            email_create.attachment,
        )

        return {"message": "Email has been sent"}

    def render_email_template(self, template_name: str, context: dict) -> str:
        """
        Render an email template using Jinja2 with the given context.

        :param template_name: Name of the template file.
        :param context: Dictionary of variables to render into the template.
        :return: Rendered email body as a string.
        """
        template = self.env.get_template(template_name)
        return template.render(context)

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
        calendar = event.calendar
        reservation_service = event.calendar.reservation_service
        user = event.user

        context = self.construct_body_context(
            event,
            user,
            reservation_service,
            calendar,
            email_meta.reason,
        )

        # Mail for club members
        template_for_member = f"{email_meta.template_name}.txt"
        body = self.render_email_template(template_for_member, context)
        email_create = self.construct_email(str(event.email), email_meta.subject, body)
        await self.send_email(email_create, background_tasks)

        # Mail for manager
        template_for_manager = f"{email_meta.template_name}_manager.txt"
        body = self.render_email_template(template_for_manager, context)
        email_subject = f"[Reservation Alert] {email_meta.subject}"
        email_create = self.construct_email(
            reservation_service.contact_mail,
            email_subject,
            body,
        )
        await self.send_email(email_create, background_tasks)

        return {"message": "Emails has been sent successfully"}

    def construct_email(
        self,
        send_to_email: str,
        subject: str,
        body: str,
    ) -> EmailCreate:
        """
        Construct the schema of the email.

        :param send_to_email: Recipient email address.
        :param subject: Email subject.
        :param body: Email body.

        :return: Constructed EmailCreate schema.
        """
        return EmailCreate(
            email=[str(send_to_email)],
            subject=subject,
            body=body,
        )

    def construct_body_context(
        self,
        event: EventLite,
        user: UserLite,
        reservation_service: ReservationServiceLite,
        calendar: CalendarLite,
        reason: str,
    ) -> dict:
        """
        Construct a dictionary of context variables to render an email template.

        :param event: EventExtra object in db.
        :param user: UserLite object in db.
        :param reservation_service: ReservationServiceDetail object in db.
        :param calendar: CalendarDetail object in db.
        :param reason: Optional reason string to include in the message.
        :return: Context dictionary for email rendering.
        """
        additional_services = "-"
        if event.additional_services:
            additional_services = ", ".join(event.additional_services)

        return {
            "reservation_type": calendar.reservation_type,
            "start_time": event.reservation_start.strftime("%d/%m/%Y, %H:%M"),
            "end_time": event.reservation_end.strftime("%d/%m/%Y, %H:%M"),
            "requested_start_time": (
                event.requested_reservation_start.strftime("%d/%m/%Y, %H:%M")
                if event.requested_reservation_start
                else None
            ),
            "requested_end_time": (
                event.requested_reservation_end.strftime("%d/%m/%Y, %H:%M")
                if event.requested_reservation_end
                else None
            ),
            "user_name": user.full_name,
            "event_guests": event.guests,
            "event_purpose": event.purpose,
            "additionals": additional_services,
            "wiki": reservation_service.web,
            "manager_email": reservation_service.contact_mail,
            "reservation_service": reservation_service.name,
            "reason": reason,
            "club_name": settings.ORGANIZATION_NAME,
        }

    def create_email_meta(self, template_name: str, subject: str, reason: str = "") -> EmailMeta:
        """
        Construct an EmailMeta object from parameters.

        :param template_name: Name of the email template.
        :param subject: Email subject.
        :param reason: Optional reason content.
        :return: EmailMeta instance.
        """
        return EmailMeta(
            template_name=template_name,
            subject=subject,
            reason=reason,
        )

    async def _send_and_cleanup(
        self, fm: FastMail, message: MessageSchema, attachment: str | None
    ) -> None:
        """
        Send an email message and clean up the attachment file after sending.

        :param fm: FastMail instance used to send the email.
        :param message: MessageSchema object containing email details.
        :param attachment: Optional file path to the attachment to be deleted after sending.
        """
        try:
            await fm.send_message(message)
        finally:
            if attachment:
                path = AsyncPath(attachment)
                if await path.exists():
                    await path.unlink()
