"""
Utils for API.
"""
import datetime as dt
from enum import Enum
from uuid import UUID
from urllib.parse import urlparse, urlunparse
import pytz
from fastapi import status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from schemas import User, Calendar, EventCreate


def modify_url_scheme(url: str, new_scheme: str) -> str:
    """
    Modify the scheme of the provided URL (e.g., change from 'http' to 'https').

    :param url: The original URL to modify.
    :param new_scheme: The new scheme to use (e.g., 'https').

    :return: The modified URL with the new scheme.
    """
    parsed_url = urlparse(url)

    # Ensure the new scheme is used
    new_url = urlunparse(
        (new_scheme, parsed_url.netloc, parsed_url.path, parsed_url.params,
         parsed_url.query, parsed_url.fragment)
    )
    return new_url


def control_collision(
        google_calendar_service,
        event_input: EventCreate,
        calendar: Calendar
) -> bool:
    """
    Check if there is already another reservation at that time.

    :param google_calendar_service: Google Calendar service.
    :param event_input: Input data for creating the event.
    :param calendar: Calendar object in db.

    :return: Boolean indicating if here is already another reservation or not.
    """
    if not calendar:
        return False

    check_collision: list = []
    collisions: list = calendar.collision_with_calendar
    collisions.append(calendar.id)
    if calendar.collision_with_calendar:
        for calendar_id in collisions:
            check_collision.extend(get_events(google_calendar_service,
                                              event_input.start_datetime,
                                              event_input.end_datetime,
                                              calendar_id))

    if not check_collision_time(check_collision,
                                event_input.start_datetime,
                                event_input.end_datetime,
                                calendar,
                                google_calendar_service):
        return False
    return True


def get_events(service, start_time, end_time, calendar_id):
    """
    Get events from Google calendar by its id

    :param service: Google Calendar service.
    :param start_time: Start time of the reservation.
    :param end_time: End time of the reservation.
    :param calendar_id: The calendar id of the Calendar object.

    :return: List of the events for that time
    """

    start_time_str = start_time.isoformat() + "+02:00"
    end_time_str = end_time.isoformat() + "+02:00"

    # Call the Calendar API
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_time_str,
        timeMax=end_time_str,
        singleEvents=True,
        orderBy='startTime',
        timeZone='Europe/Prague'
    ).execute()
    return events_result.get('items', [])


def check_collision_time(check_collision, start_datetime,
                         end_datetime, calendar: Calendar,
                         google_calendar_service) -> bool:
    """
    Check if there is already another reservation at that time.

    :param check_collision: Start time of the reservation.
    :param start_datetime: End time of the reservation.
    :param end_datetime: End time of the reservation.
    :param calendar: Calendar object in db.
    :param google_calendar_service: Google Calendar service.

    :return: Boolean indicating if here is already another reservation or not.
    """
    if not calendar.collision_with_itself:
        collisions = get_events(google_calendar_service,
                                start_datetime,
                                end_datetime, calendar.id)
        if len(collisions) > calendar.max_people:
            return False

    if len(check_collision) == 0:
        return True

    if len(check_collision) > 1:
        return False

    start_date = dt.datetime.fromisoformat(str(start_datetime))
    end_date = dt.datetime.fromisoformat(str(end_datetime))
    start_date_event = dt.datetime.fromisoformat(str(check_collision[0]['start']['dateTime']))
    end_date_event = dt.datetime.fromisoformat(str(check_collision[0]['end']['dateTime']))

    if end_date_event == start_date.astimezone(pytz.timezone('Europe/Prague')) \
            or start_date_event == end_date.astimezone(pytz.timezone('Europe/Prague')):
        return True

    return False


def check_night_reservation(
        user: User
) -> bool:
    """
    Control if user have permission for night reservation.

    :param user: User object in db.

    :return: True if user can do night reservation and false otherwise.
    """
    if not user.active_member:
        return False
    return True


def control_available_reservation_time(start_datetime, end_datetime) -> bool:
    """
    Check if a user can reserve at night.

    :param start_datetime: Start time of the reservation.
    :param end_datetime: End time of the reservation.

    :return: Boolean indicating if a user can reserve at night or not.
    """

    start_time = start_datetime.time()
    end_time = end_datetime.time()

    start_res_time = dt.datetime.strptime('08:00:00', '%H:%M:%S').time()
    end_res_time = dt.datetime.strptime('22:00:00', '%H:%M:%S').time()

    if start_time < start_res_time or end_time < start_res_time \
            or end_time > end_res_time:
        return False
    return True


class Message(BaseModel):
    """Model for response message."""
    message: str


class Entity(Enum):
    """Enum for entity names."""
    USER = "User"
    CALENDAR = "Calendar"
    EVENT = "Event"
    MINI_SERVICE = "Mini Service"
    RESERVATION_SERVICE = "Reservation Service"
    EMAIL = "Email"


# pylint: disable=unused-argument
# reason: Exception handlers require request and exception parameter.

def get_exception_response_detail(status_code: int, desc: str) -> dict:
    """Get exception response detail for openAPI documentation.

    :param status_code: Status code of the exception.
    :param desc: Description of the exception.

    :return dict: Exception response detail.
    """
    return {
        status_code: {
            "model": Message,
            "description": desc
        }
    }


class MethodNotAllowedException(Exception):
    """Exception for not allowed methods."""
    STATUS_CODE = status.HTTP_405_METHOD_NOT_ALLOWED
    DESCRIPTION = "Method not allowed."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(self, entity: Entity):
        self.entity = entity


def method_not_allowed_exception_handler(
        request: Request, exc: MethodNotAllowedException
) -> JSONResponse:
    """Exception handler for MethodNotAllowedException.

    :param request: Request that caused the exception.
    :param exc: The exception.
    """
    return JSONResponse(
        status_code=exc.STATUS_CODE,
        content={
            "message": f"Method {request.method} is not allowed for entity {exc.entity.value}"
        },
    )


class EntityNotFoundException(Exception):
    """
    Exception for when entity is not found in database.
    """
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DESCRIPTION = "Entity not found."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)

    def __init__(self, entity: Entity, entity_id: UUID | str):
        self.entity = entity
        self.entity_uuid = entity_id


def entity_not_found_exception_handler(
        request: Request, exc: EntityNotFoundException
) -> JSONResponse:
    """Exception handler for EntityNotFoundException.

    :param request: Request that caused the exception.
    :param exc: The exception.
    """
    return JSONResponse(
        status_code=exc.STATUS_CODE,
        content={
            "message": f"Entity {exc.entity.value} with id {exc.entity_uuid} "
                       f"was not found or you don't "
                       f"have permission to do operation with that entity."
        },
    )


class NotImplementedException(Exception):
    """Exception for when a functionality is not yet implemented."""
    STATUS_CODE = status.HTTP_501_NOT_IMPLEMENTED
    DESCRIPTION = "Method not implemented."
    RESPONSE = get_exception_response_detail(STATUS_CODE, DESCRIPTION)


def not_implemented_exception_handler(
        request: Request, exc: NotImplementedException
) -> JSONResponse:
    """Exception handler for NotImplementedException.

    :param request: Request that caused the exception.
    :param exc: The exception.
    """
    return JSONResponse(
        status_code=exc.STATUS_CODE,
        content={
            "message": exc.DESCRIPTION
        },
    )


# pylint: disable=too-few-public-methods
# reason: no more public methods needed.
class FastApiDocs:
    """Information for fastapi documentation."""
    NAME = "Reservation System of the Buben Club"
    DESCRIPTION = \
        "Reservation System of the Buben Club API is " \
        "a REST API that offers you an access to our " \
        "application!"
    VERSION = "1.0.0"
    AUTHORISATION_TAG = {
        "name": "users",
        "description": "Authorisation in IS.",
    }
    RESERVATION_SERVICE_TAG = {
        "name": "reservation services",
        "description": "Operations with reservation services.",
    }
    CALENDAR_TAG = {
        "name": "calendars",
        "description": "Operations with calendars.",
    }
    MINI_SERVICE_TAG = {
        "name": "mini services",
        "description": "Operations with mini services.",
    }
    EVENT_TAG = {
        "name": "events",
        "description": "Operations with events.",
    }
    EMAIL_TAG = {
        "name": "emails",
        "description": "Operations with emails.",
    }

    def get_tags_metadata(self):
        """Get tags metadata."""
        return [
            self.AUTHORISATION_TAG,
            self.RESERVATION_SERVICE_TAG,
            self.CALENDAR_TAG,
            self.MINI_SERVICE_TAG,
            self.EVENT_TAG,
            self.EMAIL_TAG
        ]


fastapi_docs = FastApiDocs()

# pylint: enable=too-few-public-methods
