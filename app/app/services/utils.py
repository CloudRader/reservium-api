"""
Utils for services.
"""
import datetime as dt
import pytz

from models import CalendarModel
from schemas import Rules, EventCreate, InformationFromIS


def control_conditions_and_permissions(user, is_buk, event_input: EventCreate,
                                       google_calendar_service, calendar: CalendarModel):
    """
    Check conditions and permissions for creating an event.

    :param user: User object in db.
    :param is_buk: Information about user from IS.
    :param event_input: Input data for creating the event.
    :param google_calendar_service: Google Calendar service.
    :param calendar: Calendar object in db.

    :return: Message indicating whether access is granted or denied.
    """

    # Check of the membership
    standard_message = first_standard_check(is_buk, calendar, event_input.start_datetime)
    if not standard_message == "Access":
        return standard_message

    # Choose user rules
    user_rules = choose_user_rules(user, calendar)

    # Check available reservation time
    if not user_rules.night_time:
        if not control_available_reservation_time(event_input.start_datetime,
                                                  event_input.end_datetime):
            return {"message": "You can't make reservations at night!"}

    # Check collision with other reservation
    check_collision: list = []
    if calendar.collision_with_calendar:
        for calendar_id in calendar.collision_with_calendar:
            check_collision.extend(get_events(google_calendar_service,
                                              event_input.start_datetime,
                                              event_input.end_datetime,
                                              calendar_id))

    if not check_collision_time(check_collision,
                                event_input.start_datetime,
                                event_input.end_datetime,
                                calendar,
                                google_calendar_service):
        return {"message": "There's already a reservation for that time."}

    # Reservation no more than 24 hours
    if not dif_days_res(event_input.start_datetime, event_input.end_datetime, user_rules):
        return {"message": "You can reserve on different day."}

    # Check reservation in advance and prior
    message = reservation_in_advance(event_input.start_datetime, user_rules)
    if not message == "Access":
        return message

    return "Access"


def first_standard_check(is_buk, calendar, start_time):
    """
    Checking if the user is reserving the service user has
    and that user can't reserve before current date.

    :param is_buk: Information about user from IS.
    :param calendar: Calendar object in db.
    :param start_time: Start time of the reservation.

    :return: True indicating if the reservation
    is made rightly or message if not.
    """
    # Check of the membership
    if not service_availability_check(is_buk.services, calendar.service_alias):
        return {"message": f"You don't have {calendar.service_alias} service!"}

    # Check error reservation
    if start_time < dt.datetime.now():
        return {"message": "You can't make a reservation before the present time!"}

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
                           f"{user_rules.in_advance_day} days "
                           f"in advance!"}

    return "Access"


def choose_user_rules(user, calendar):
    """
    Choose user rules based on the calendar rules and user roles.

    :param user: User object in db.
    :param calendar: Calendar object in db.

    :return: Rules object.
    """

    if not user.active_member:
        return Rules(**calendar.club_member_rules)
    if calendar.service_alias in user.roles:
        return Rules(**calendar.manager_rules)
    return Rules(**calendar.active_member_rules)


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
    if not user_rules.reservation_more_24_hours:
        time_difference = abs(end_datetime - start_datetime)
        if time_difference > dt.timedelta(hours=24):
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
        if time_difference > dt.timedelta(days=user_rules.in_advance_day):
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


def check_collision_time(check_collision, start_datetime,
                         end_datetime, calendar: CalendarModel,
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
                                end_datetime, calendar.calendar_id)
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

    if end_date_event == start_date.astimezone(pytz.timezone('Europe/Vienna')) \
            or start_date_event == end_date.astimezone(pytz.timezone('Europe/Vienna')):
        return True

    return False


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
        f"Jméno/Name: {user.first_name} {user.surname}\n"
        f"Pokoj/Room: {room.door_number}\n"
        f"Číslo osob/Participants: {event_input.guests}\n"
        f"Účel/Purpose: {event_input.purpose}\n"
        f"\n"
        f"Další služby/Add. services: {formatted_services}\n"
    )


def ready_event(calendar: CalendarModel, event_input: EventCreate,
                is_buk: InformationFromIS):
    """
    Constructing the body of the event .

    :param calendar: Calendar object in db.
    :param event_input: Input data for creating the event.
    :param is_buk: Information about user from IS.

    :return: Dict body of the event.
    """

    start_time = event_input.start_datetime.isoformat()
    end_time = event_input.end_datetime.isoformat()
    return {
        "summary": calendar.event_name,
        "description": description_of_event(is_buk.user, is_buk.room, event_input),
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
