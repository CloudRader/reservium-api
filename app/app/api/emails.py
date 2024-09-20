"""
API controllers for emails.
"""
from typing import Any

from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi import APIRouter, status
from api import fastapi_docs
from schemas import EmailCreate
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
        recipients=[email_create.email],  # List of recipients
        body=email_create.body,
        subtype=MessageType.plain
    )

    fm = FastMail(email_connection)
    # background_tasks.add_task(fm.send_message, message)
    await fm.send_message(message)
    return {"message": "Email has been sent"}
