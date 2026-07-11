"""OpenID-specific service integrations."""

from infrastructure.identity.openid.provider import OpenIdProvider
from infrastructure.identity.openid.schemas import UserInfo

__all__ = [
    "OpenIdProvider",
    "UserInfo",
]
