"""IS-specific service integrations with Authentication."""

from integrations.information_system.is_auth import IsAuthService
from integrations.information_system.is_services import IsService

__all__ = [
    "IsAuthService",
    "IsService",
]
