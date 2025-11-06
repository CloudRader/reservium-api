"""
Define an abstract base class AbstractEmailService.

This class works with Email.
"""

import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from core import settings
from core.schemas import EmailCreate, RegistrationFormCreate, UserLite
from pypdf import PdfReader, PdfWriter


class AbstractEmailService(ABC):
    """Abstract class defines the interface for an email service."""

    @abstractmethod
    def prepare_registration_form(
        self,
        registration_form: RegistrationFormCreate,
        full_name: UserLite,
    ) -> Any:
        """
        Prepare registration form in pdf for sending to head of the dormitory.

        :param registration_form: Input data for adding in pdf.
        :param full_name: UserLite fullname.

        :returns EventExtra json object: the created event or exception otherwise.
        """


class EmailService(AbstractEmailService):
    """Class EmailService represent service that work with Email."""

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
