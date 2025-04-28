"""
Module for testing email service.
"""
import pytest


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


@pytest.mark.asyncio
def test_prepare_registration_form(registration_form_create,
                                   service_email):
    """
    Test creating a registration form for sending by email.
    """
    registration_form = service_email.prepare_registration_form(
        registration_form_create, "John Doll"
    )
    assert registration_form.subject == "Event Registration"
    assert registration_form.attachment == "/tmp/event_registration.pdf"
    assert registration_form_create.email in registration_form.email
    assert registration_form_create.manager_contact_mail in registration_form.email
    assert registration_form.body == "Request to reserve an event for a member John Doll"
