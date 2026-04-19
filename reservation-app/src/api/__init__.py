"""Package for API modules."""

from .dependencies import get_current_user
from .permissions import (
    abac_event_owner_by_id,
    abac_manage_rs_by_id,
    abac_manage_rs_from_body,
    require_permission,
)

__all__ = [
    "abac_event_owner_by_id",
    "abac_manage_rs_by_id",
    "abac_manage_rs_from_body",
    "get_current_user",
    "require_permission",
]
