"""
Utils for API.
"""
import datetime as dt
from urllib.parse import urlparse, urlunparse
from pytz import timezone
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
    prague = timezone("Europe/Prague")

    start_time_str = prague.localize(start_time).isoformat()
    end_time_str = prague.localize(end_time).isoformat()

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

    if end_date_event == start_date.astimezone(timezone('Europe/Prague')) \
            or start_date_event == end_date.astimezone(timezone('Europe/Prague')):
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
