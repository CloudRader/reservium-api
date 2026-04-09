"""API controllers for emails."""

from typing import Annotated, Any

from api import get_current_user
from core.schemas import (
    RegistrationFormCreate,
    UserLite,
)
from fastapi import APIRouter, BackgroundTasks, Depends, status
from services import EmailService

router = APIRouter()


@router.post(
    "/send-registration-form",
    status_code=status.HTTP_201_CREATED,
)
async def send_registration_form(
    service: Annotated[EmailService, Depends(EmailService)],
    user: Annotated[UserLite, Depends(get_current_user)],
    registration_form: RegistrationFormCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Send email with PDF attachment with reservation request to dorm head's email address.

    :param service: Email service.
    :param user: UserLite who make this request.
    :param registration_form: RegistrationFormCreate schema.
    :param background_tasks: BackgroundTasks object used to run the email sending asynchronously.

    :returns Dictionary: Confirming that the registration form has been sent.
    """
    email_create = service.prepare_registration_form(registration_form, user.full_name)

    await service.send_email(email_create, background_tasks)

    return {"message": "Registration form has been sent"}
