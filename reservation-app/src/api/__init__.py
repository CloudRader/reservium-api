"""Package for API modules."""

from .dependencies import (
    get_calendar_service,
    get_current_user,
    get_current_user_from_token,
    get_event_service,
    get_identity_provider,
    get_mini_service_service,
    get_reservation_service_service,
    get_user_service,
)
from .permissions import (
    abac_event_owner_by_id,
    abac_event_owner_or_manager,
    abac_manage_rs_by_id,
    abac_manage_rs_from_body,
    require_permission,
)

__all__ = [
    "abac_event_owner_by_id",
    "abac_event_owner_or_manager",
    "abac_manage_rs_by_id",
    "abac_manage_rs_from_body",
    "get_calendar_service",
    "get_current_user",
    "get_current_user_from_token",
    "get_event_service",
    "get_identity_provider",
    "get_mini_service_service",
    "get_reservation_service_service",
    "get_user_service",
    "require_permission",
]
