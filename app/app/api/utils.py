"""Utils for API."""

import datetime as dt
from urllib.parse import urlparse, urlunparse

from api.external_api.google.google_calendar_services import GoogleCalendarService
from api.v1.emails import create_email_meta, preparing_email
from core.models import EventState
from core.schemas import Calendar, EventCreate, ReservationService, User
from pytz import timezone
from services import EventService


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
        (
            new_scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        ),
    )
    return new_url


async def control_collision(
    google_calendar_service,
    event_input: EventCreate,
    calendar: Calendar,
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
            check_collision.extend(
                await google_calendar_service.fetch_events_in_time_range(
                    event_input.start_datetime,
                    event_input.end_datetime,
                    calendar_id,
                ),
            )

    return await check_collision_time(
        check_collision,
        event_input.start_datetime,
        event_input.end_datetime,
        calendar,
        google_calendar_service,
    )


async def check_collision_time(
    check_collision,
    start_datetime,
    end_datetime,
    calendar: Calendar,
    google_calendar_service,
) -> bool:
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
        collisions = await google_calendar_service.fetch_events_in_time_range(
            google_calendar_service,
            start_datetime,
            end_datetime,
            calendar.id,
        )
        if len(collisions) > calendar.max_people:
            return False

    if len(check_collision) == 0:
        return True

    if len(check_collision) > 1:
        return False

    start_date = dt.datetime.fromisoformat(str(start_datetime))
    end_date = dt.datetime.fromisoformat(str(end_datetime))
    start_date_event = dt.datetime.fromisoformat(
        str(check_collision[0]["start"]["dateTime"]),
    )
    end_date_event = dt.datetime.fromisoformat(
        str(check_collision[0]["end"]["dateTime"]),
    )

    return bool(
        end_date_event == start_date.astimezone(timezone("Europe/Prague"))
        or start_date_event == end_date.astimezone(timezone("Europe/Prague")),
    )


def check_night_reservation(user: User) -> bool:
    """
    Control if user have permission for night reservation.

    :param user: User object in db.

    :return: True if user can do night reservation and false otherwise.
    """
    return user.active_member


def control_available_reservation_time(start_datetime, end_datetime) -> bool:
    """
    Check if a user can reserve at night.

    :param start_datetime: Start time of the reservation.
    :param end_datetime: End time of the reservation.

    :return: Boolean indicating if a user can reserve at night or not.
    """
    start_time = start_datetime.time()
    end_time = end_datetime.time()

    start_res_time = dt.datetime.strptime("08:00:00", "%H:%M:%S").time()
    end_res_time = dt.datetime.strptime("22:00:00", "%H:%M:%S").time()

    return not (start_time < start_res_time or end_time < start_res_time or end_time > end_res_time)


async def process_event_approval(
    service: EventService,
    user: User,
    calendar: Calendar,
    event_body: dict,
    event_create: EventCreate,
    reservation_service: ReservationService,
):
    """
    Approve or reject the event based on guest count and time rules.

    Creates the event in Google Calendar and updates the local event state accordingly.
    Sends notification emails if the event is approved or not.

    :param service: Event service.
    :param user: User who make this request.
    :param calendar: Calendar object in db.
    :param event_body: Google Calendar-compatible event data.
    :param event_create: EventCreate schema.
    :param reservation_service: Reservation Service object in db.

    :return: Either a Google Calendar event object if approved,
             or a dictionary with a rejection message.
    """
    google_calendar_service = GoogleCalendarService()

    if event_create.guests > calendar.max_people:
        event_body["summary"] = f"Not approved - more than {calendar.max_people} people"
    elif not check_night_reservation(user) and not control_available_reservation_time(
        event_create.start_datetime,
        event_create.end_datetime,
    ):
        event_body["summary"] = "Not approved - night time"
    else:
        event_google_calendar = await google_calendar_service.insert_event(calendar.id, event_body)
        event = await service.create_event(
            event_create,
            user,
            EventState.CONFIRMED,
            event_google_calendar["id"],
        )
        await preparing_email(
            service,
            event,
            create_email_meta(
                "confirm_reservation",
                f"{reservation_service.name} Reservation Confirmation",
            ),
        )
        return event_google_calendar

    event_summary = event_body["summary"]
    event_google_calendar = await google_calendar_service.insert_event(
        event_create.calendar_id, event_body
    )
    event = await service.create_event(
        event_create,
        user,
        EventState.NOT_APPROVED,
        event_google_calendar["id"],
    )

    if "night time" in event_summary.lower():
        await preparing_email(
            service,
            event,
            create_email_meta("not_approve_night_time_reservation", event_summary),
        )
    return {"message": event_summary}
