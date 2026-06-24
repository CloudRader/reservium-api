"""DTO schemes for Well Known response."""

from typing import Literal

from pydantic import BaseModel


class WellKnownResponse(BaseModel):
    """Well Known Response schema."""

    status: Literal["Ok"]
