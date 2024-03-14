"""
Package for Services.
"""
# from .service_base import AbstractCRUDService, CrudServiceBase
from .event_services import AbstractEventService, EventService

__all__ = [
    # "AbstractCRUDService", "CrudServiceBase",
    "AbstractEventService", "EventService"
]
