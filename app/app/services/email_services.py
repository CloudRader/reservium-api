"""
This module defines an abstract base class AbstractEmailService that work with Email.
"""
import shutil
import os

from typing import Any
from datetime import datetime
from abc import ABC, abstractmethod

from schemas import RegistrationFormCreate, User, EmailCreate
from pypdf import PdfReader, PdfWriter


# pylint: disable=too-few-public-methods
# reason: Methods will be added in the next versions of the program
class AbstractEmailService(ABC):
    """
    This abstract class defines the interface for an email service.
    """

    @abstractmethod
    def prepare_registration_form(
            self, registration_form: RegistrationFormCreate,
            full_name: User
    ) -> Any:
        """
        Preparing registration form in pdf for sending to head of the dormitory.
        :param registration_form: Input data for adding in pdf.
        :param full_name: User fullname.

        :returns Event json object: the created event or exception otherwise.
        """


class EmailService(AbstractEmailService):
    """
    Class EmailService represent service that work with Email
    """

    def prepare_registration_form(
            self, registration_form: RegistrationFormCreate,
            full_name: str
    ) -> EmailCreate:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        original_pdf_path = os.path.join(base_dir, '..', 'templates', 'event_registration.pdf')
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
            }
        )

        # Save the filled PDF
        with open(output_path, "wb") as output_pdf:
            writer.write(output_pdf)

        email_create = EmailCreate(
            email=[registration_form.email, registration_form.manager_contact_mail],
            subject="Event Registration",
            body=(
                f"Request to reserve an event for a member {full_name}"
            ),
            attachment=output_path
        )

        return email_create
