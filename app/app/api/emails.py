"""
API controllers for emails.
"""
from typing import Any, Annotated
import os

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi import APIRouter, status, Depends
from api import get_current_token, get_request
from schemas import EmailCreate, RegistrationFormCreate, UserIS, User, Event, \
    EmailMeta
from models import ReservationServiceModel, CalendarModel
from services import EmailService, EventService
from core import email_connection
from .docs import fastapi_docs

router = APIRouter(
    prefix='/emails',
    tags=[fastapi_docs.EMAIL_TAG["name"]]
)

template_dir = Path(__file__).parent.parent / "templates" / "email"
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape()
)


def render_email_template(template_name: str, context: dict) -> str:
    """
    Renders an email template using Jinja2 with the given context.

    :param template_name: Name of the template file.
    :param context: Dictionary of variables to render into the template.
    :return: Rendered email body as a string.
    """
    template = env.get_template(template_name)
    return template.render(context)


@router.post("/send_registration_form",
             status_code=status.HTTP_201_CREATED,
             )
async def send_registration_form(
        service: Annotated[EmailService, Depends(EmailService)],
        token: Annotated[Any, Depends(get_current_token)],
        registration_form: RegistrationFormCreate
) -> Any:
    """
    Sends email with pdf attachment with reservation request to
    dorm head's email address.

    :param service: Email service.
    :param token: Token for user identification.
    :param registration_form: RegistrationFormCreate schema.

    :returns Dictionary: Confirming that the registration form has been sent.
    """
    user_is = UserIS.model_validate(await get_request(token, "/users/me"))
    full_name = user_is.first_name + " " + user_is.surname
    email_create = service.prepare_registration_form(registration_form, full_name)

    await send_email(email_create)

    if email_create.attachment and os.path.exists(email_create.attachment):
        os.remove(email_create.attachment)

    return {"message": "Registration form has been sent"}


async def send_email(
        email_create: EmailCreate
) -> Any:
    """
    Sends an email asynchronously.

    This endpoint sends an email using the provided email details. The email is
    sent in the background to avoid blocking the request-response cycle.

    :param email_create: Email Create schema.

    :returns Dictionary: Confirming that the email has been sent.
    """
    message = MessageSchema(
        subject=email_create.subject,
        recipients=email_create.email,  # List of recipients
        body=email_create.body,
        subtype=MessageType.plain,
        attachments=[email_create.attachment] if email_create.attachment else []
    )

    fm = FastMail(email_connection)
    # background_tasks.add_task(fm.send_message, message)
    await fm.send_message(message)

    if email_create.attachment and os.path.exists(email_create.attachment):
        os.remove(email_create.attachment)

    return {"message": "Email has been sent"}


async def preparing_email(
        service_event: Annotated[EventService, Depends(EventService)],
        event: Event,
        email_meta: EmailMeta
) -> Any:
    """
    Prepares and sends both member and manager information email based on an event.

    :param service_event: Event service to resolve event relationships.
    :param event: The Event object in db.
    :param email_meta: Email metadata containing template name, subject and reason.
    :return: Dictionary confirming the emails have been sent.
    """
    calendar = await service_event.get_calendar_of_this_event(event)
    reservation_service = await service_event.get_reservation_service_of_this_event(event)
    user = await service_event.get_user_of_this_event(event)

    context = construct_body_context(
        event, user, reservation_service, calendar, email_meta.reason
    )

    # Mail for club members
    template_for_member = f"{email_meta.template_name}.txt"
    body = render_email_template(template_for_member, context)
    email_create = construct_email(event.email, email_meta.subject, body)
    await send_email(email_create)

    # Mail for manager
    template_for_manager = f"{email_meta.template_name}_manager.txt"
    body = render_email_template(template_for_manager, context)
    email_subject = f"[Reservation Alert] {email_meta.subject}"
    email_create = construct_email(reservation_service.contact_mail, email_subject, body)
    await send_email(email_create)

    return {"message": "Emails has been sent successfully"}


def construct_email(
        send_to_email: str,
        subject: str,
        body: str,
) -> EmailCreate:
    """
    Constructing the schema of the email .

    :param send_to_email: Recipient email address.
    :param subject: Email subject.
    :param body: Email body.

    :return: Constructed EmailCreate schema.
    """

    return EmailCreate(
        email=[send_to_email],
        subject=subject,
        body=body,
    )


def construct_body_context(
        event: Event,
        user: User,
        reservation_service: ReservationServiceModel,
        calendar: CalendarModel,
        reason: str,
) -> dict:
    """
    Constructs a dictionary of context variables to render an email template.

    :param event: Event object in db.
    :param user: User object in db.
    :param reservation_service: ReservationService object in db.
    :param calendar: Calendar object in db.
    :param reason: Optional reason string to include in the message.
    :return: Context dictionary for email rendering.
    """
    additional_services = "-"
    if event.additional_services:
        additional_services = ", ".join(event.additional_services)

    context = {
        "reservation_type": calendar.reservation_type,
        "start_time": event.start_datetime.strftime("%d/%m/%Y, %H:%M"),
        "end_time": event.end_datetime.strftime("%d/%m/%Y, %H:%M"),
        "user_name": user.full_name,
        "user_room": user.room_number,
        "event_guests": event.guests,
        "event_purpose": event.purpose,
        "additionals": additional_services,
        "wiki": reservation_service.web,
        "manager_email": reservation_service.contact_mail,
        "reservation_service": reservation_service.name,
        "reason": reason,
    }

    return context


def create_email_meta(
        template_name: str,
        subject: str,
        reason: str = ""
) -> EmailMeta:
    """
    Constructs an EmailMeta object from parameters.

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
