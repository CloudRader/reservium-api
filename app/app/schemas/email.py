"""
DTO schemes for Email entity.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class EmailCreate(BaseModel):
    """Schema for creating an email."""
    email: EmailStr
    subject: str
    body: str
    attachment: Optional[str] = None
