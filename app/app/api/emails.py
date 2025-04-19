"""
API controllers for emails.
"""
from typing import Any, Annotated
import os

from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi import APIRouter, status, Depends
from api import fastapi_docs, get_current_token, get_request
from schemas import EmailCreate, RegistrationFormCreate, UserIS
from services import EmailService
from core import email_connection

router = APIRouter(
    prefix='/emails',
    tags=[fastapi_docs.EMAIL_TAG["name"]]
)


@router.post("/send_email",
             status_code=status.HTTP_201_CREATED,
             )
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
