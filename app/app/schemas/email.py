"""
DTO schemes for Email entity.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class EmailCreate(BaseModel):
    """Schema for creating an email."""
    email: List[EmailStr]
    subject: str
    body: str
    attachment: Optional[str] = None


class EmailMeta(BaseModel):
    """Meta information for creating an email."""
    template_name: str
    subject: str
    reason: str


class RegistrationFormCreate(BaseModel):
    """Schema for creating a registration form."""
    event_name: str = Field(max_length=40)
    guests: int = Field(ge=1)
    event_start: datetime
    event_end: datetime
    email: EmailStr
    organizers: str
    space: str
    other_space: List[str]
    manager_contact_mail: EmailStr
