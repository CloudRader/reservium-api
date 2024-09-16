"""
Utils for services.
"""
import datetime as dt

from models import CalendarModel, ReservationServiceModel
from schemas import Rules, EventCreate, InformationFromIS


def first_standard_check(
        is_info: InformationFromIS,
        reservation_service: ReservationServiceModel,
        start_time, end_time
):
    """
    Checking if the user is reserving the service user has
    and that user can't reserve before current date.

    :param is_info: Information about user from IS.
    :param reservation_service: Reservation Service object in db.
    :param start_time: Start time of the reservation.
    :param end_time: End time of the reservation.

    :return: True indicating if the reservation
    is made rightly or message if not.
    """
    # Check of the membership
    if not service_availability_check(is_info.services, reservation_service.alias):
        return {"message": f"You don't have {reservation_service.alias} service!"}

    # Check error reservation
    if start_time < dt.datetime.now():
        return {"message": "You can't make a reservation before the present time!"}

    if end_time < start_time:
        return {"message": "The end of a reservation cannot be before its beginning!"}

    return "Access"


def reservation_in_advance(start_time, user_rules):
    """
    Check if the reservation is made within the specified advance and prior time.

    :param start_time: Start time of the reservation.
    :param user_rules: Rules object containing reservation rules.
    reservation is made in advance or in prior.

    :return: True indicating if the reservation
    is made within the specified advance or prior time or message if not.
    """
    # Reservation in advance
    if not control_res_in_advance_or_prior(start_time, user_rules, True):
        return {"message": f"You have to make reservations "
                           f"{user_rules.in_advance_hours} hours and "
                           f"{user_rules.in_advance_minutes} minutes in advance!"}

    # Reservation prior than
    if not control_res_in_advance_or_prior(start_time, user_rules, False):
        return {"message": f"You can't make reservations earlier than "
                           f"{user_rules.in_prior_days} days "
                           f"in advance!"}

    return "Access"


def dif_days_res(start_datetime, end_datetime, user_rules: Rules) -> bool:
    """
    Check if the reservation duration is less than 24 hours.

    :param start_datetime: Start datetime of the reservation.
    :param end_datetime: End datetime of the reservation.
    :param user_rules: Rules object containing reservation rules.

    :return: Boolean indicating if the reservation duration is less than 24
    """

    if start_datetime.year != end_datetime.year \
            or start_datetime.month != end_datetime.month:
        return False

    time_difference = abs(end_datetime - start_datetime)
    if time_difference > dt.timedelta(hours=user_rules.max_reservation_hours):
        return False
    return True


def control_res_in_advance_or_prior(start_time, user_rules: Rules,
                                    in_advance: bool) -> bool:
    """
    Check if the reservation is made within the specified advance or prior time.

    :param start_time: Start time of the reservation.
    :param user_rules: Rules object containing reservation rules.
    :param in_advance: Boolean indicating whether to check if the
    reservation is made in advance or in prior.

    :return: Boolean indicating if the reservation
    is made within the specified advance or prior time.
    """

    current_time = dt.datetime.now()

    time_difference = abs(start_time - current_time)

    if in_advance:
        if time_difference < dt.timedelta(minutes=user_rules.in_advance_minutes,
                                          hours=user_rules.in_advance_hours):
            return False
    else:
        if time_difference > dt.timedelta(days=user_rules.in_prior_days):
            return False
    return True


def description_of_event(user, room, event_input: EventCreate):
    """
    Description of the event.

    :param user: User object from IS.
    :param room: Room object from IS.
    :param event_input: Input data for creating the event.

    :return: String of the description.
    """

    formatted_services: str = "-"
    if event_input.additional_services:
        formatted_services = ", ".join(event_input.additional_services)
    return (
        f"Name: {user.first_name} {user.surname}\n"
        f"Room: {room.door_number}\n"
        f"Participants: {event_input.guests}\n"
        f"Purpose: {event_input.purpose}\n"
        f"\n"
        f"Additionals: {formatted_services}\n"
    )


def ready_event(calendar: CalendarModel, event_input: EventCreate,
                is_info: InformationFromIS):
    """
    Constructing the body of the event .

    :param calendar: Calendar object in db.
    :param event_input: Input data for creating the event.
    :param is_info: Information about user from IS.

    :return: Dict body of the event.
    """

    start_time = event_input.start_datetime.isoformat()
    end_time = event_input.end_datetime.isoformat()
    return {
        "summary": calendar.reservation_type,
        "description": description_of_event(is_info.user, is_info.room, event_input),
        "start": {
            "dateTime": start_time,
            "timeZone": "Europe/Prague"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Europe/Prague"
        },
        "attendees": [
            {"email": event_input.email},
        ],
    }


def service_availability_check(services, service_alias) -> bool:
    """
    Checking if the user is reserving the service user has.

    :param services: List of available user services on IS.
    :param service_alias: The alias of the service user wants to reserve .

    :return: Boolean indicating if a user have this service or not.
    """

    for service in services:
        if service.service.alias == service_alias:
            return True
    return False
