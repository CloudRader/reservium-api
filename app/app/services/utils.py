import datetime as dt
import pytz

from models import CalendarModel
from schemas import Rules


def control_conditions_and_permissions(user, services, event_input, google_calendar_service, calendar: CalendarModel):
    # Check of the membership
    if not service_availability_check(services, calendar.service_alias):
        return {"message": f"You don't have {calendar.service_alias} service!"}

    start_datetime = dt.datetime.strptime(event_input.start_datetime, '%Y-%m-%dT%H:%M:%S')
    end_datetime = dt.datetime.strptime(event_input.end_datetime, '%Y-%m-%dT%H:%M:%S')

    # Check error reservation
    if start_datetime < dt.datetime.now():
        return {"message": "You can't make a reservation before the present time!"}

    # Choose user rules
    user_rules: Rules = choose_user_rules(calendar, user)

    # Check available reservation time
    if not user_rules.night_time:
        if not control_available_reservation_time(start_datetime, end_datetime):
            return {"message": "You can't reserve in this gap!"}

    # Check collision with other reservation
    check_collision: list = []
    for calendar_id in calendar.collision_with_calendar:
        check_collision.extend(get_events(google_calendar_service,
                                          event_input.start_datetime,
                                          event_input.end_datetime, calendar_id))

    if not check_collision_time(check_collision, start_datetime, end_datetime):
        return {"message": "There's already a reservation for that time."}

    # Reservation no more than 24 hours
    if not dif_days_res(start_datetime, end_datetime, user_rules):
        return {"message": "You can reserve on different day."}

    # Reservation in advance
    if not control_res_in_advance(start_datetime, user_rules, True):
        return {"message": f"You have to make reservations {user_rules.in_advance_day} day,"
                           f"{user_rules.in_advance_hours} hours and"
                           f"{user_rules.in_advance_minutes} minutes in advance!"}

    # Reservation prior than
    if not control_res_in_advance(start_datetime, user_rules, False):
        return {"message": f"You can't make reservations earlier than {user_rules.in_advance_day} days "
                           f"in advance!"}

    return "Access"


def choose_user_rules(calendar, user) -> Rules:
    if not user.active_member:
        return Rules(**calendar.club_member_rules)
    if calendar.service_alias in user.roles:
        return Rules(**calendar.manager_rules)
    return Rules(**calendar.active_member_rules)


def dif_days_res(start_datetime, end_datetime, user_rules: Rules):
    if start_datetime.year != end_datetime.year \
            or start_datetime.month != end_datetime.month:
        return False
    if not user_rules.reservation_more_24_hours:
        time_difference = abs(end_datetime - start_datetime)
        if time_difference > dt.timedelta(hours=24):
            return False
    return True


def control_res_in_advance(start_time, user_rules: Rules, in_advance: bool):
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


def control_available_reservation_time(start_datetime, end_datetime):
    start_time = start_datetime.time()
    end_time = end_datetime.time()

    start_res_time = dt.datetime.strptime('08:00:00', '%H:%M:%S').time()
    end_res_time = dt.datetime.strptime('22:00:00', '%H:%M:%S').time()

    if start_time < start_res_time or end_time < start_res_time \
            or end_time > end_res_time:
        return False
    return True


def check_collision_time(check_collision, start_datetime, end_datetime):
    if len(check_collision) > 1:
        return False
    elif len(check_collision) > 0:

        start_date = dt.datetime.fromisoformat(str(start_datetime))
        end_date = dt.datetime.fromisoformat(str(end_datetime))
        start_date_event = dt.datetime.fromisoformat(str(check_collision[0]['start']['dateTime']))
        end_date_event = dt.datetime.fromisoformat(str(check_collision[0]['end']['dateTime']))

        if end_date_event == start_date.astimezone(pytz.timezone('Europe/Vienna')) \
                or start_date_event == end_date.astimezone(pytz.timezone('Europe/Vienna')):
            return True
        else:
            return False
    return True


def get_events(service, start_time, end_time, calendar_id):
    # Call the Calendar API
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_time + 'Z',
        timeMax=end_time + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])


def description_of_event(user_is, room, event_input):
    return (
        f"Jméno/Name: {user_is.first_name} {user_is.surname}\n"
        f"Pokoj/Room: {room.door_number}\n"
        f"Číslo osob/Participants: {event_input.guests}\n"
        f"Účel/Purpose: {event_input.purpose}\n"
    )


def ready_event(calendar: CalendarModel, event_input, user_is, room):
    return {
        "summary": calendar.event_name,
        "description": description_of_event(user_is, room, event_input),
        "start": {
            "dateTime": event_input.start_datetime,
            "timeZone": "Europe/Vienna"
        },
        "end": {
            "dateTime": event_input.end_datetime,
            "timeZone": "Europe/Vienna"
        },
    }


def service_availability_check(services, service_name):
    for item in services:
        if "service" in item and "name" in item["service"] and item["service"]["alias"] == service_name:
            return True
    return False
