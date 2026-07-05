"""OpenID-specific service integrations."""

from infrastructure.openid.openid_auth import OpenIdProvider
from infrastructure.openid.openid_schemas import UserInfo

__all__ = [
    "OpenIdProvider",
    "UserInfo",
]
