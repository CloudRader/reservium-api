import datetime as dt
import pytz


def control_conditions_and_permissions(services, event_input, service, calendar):
    # Check of the membership
    if not check_membership(services):
        return {"message": "You are not member of the club!"}

    start_datetime = dt.datetime.strptime(event_input.start_datetime, '%Y-%m-%dT%H:%M:%S')
    end_datetime = dt.datetime.strptime(event_input.end_datetime, '%Y-%m-%dT%H:%M:%S')

    # Check error reservation
    if start_datetime < dt.datetime.now():
        return {"message": "You can't make a reservation before the present time!"}

    # Check available reservation time
    if not control_available_reservation_time(start_datetime, end_datetime):
        return {"message": "You can't reserve in this gap!"}

    # Check collision with other reservation
    check_collision = get_events(service,
                                 event_input.start_datetime,
                                 event_input.end_datetime, calendar)

    if not check_collision_time(check_collision, start_datetime, end_datetime):
        return {"message": "There's already a reservation for that time."}

    # Reservation no more than 24 hours
    if not dif_days_res(start_datetime, end_datetime):
        return {"message": "You can reserve on different day."}

    # Reservation in advance
    if not control_res_in_advance(start_datetime):
        return {"message": "You have to make reservations 24 hours in advance!"}

    return "Access"


def dif_days_res(start_datetime, end_datetime):
    print(start_datetime.year)
    print(end_datetime.year)
    if start_datetime.year != end_datetime.year \
            or start_datetime.month != end_datetime.month \
            or start_datetime.day != end_datetime.day:
        return False
    return True


def control_res_in_advance(start_time):
    current_time = dt.datetime.now()

    time_difference = abs(start_time - current_time)

    if time_difference < dt.timedelta(hours=24):
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


def get_events(service, start_time, end_time, calendar):
    # Call the Calendar API
    events_result = service.events().list(
        calendarId=calendar["calendar_id"],
        timeMin=start_time + 'Z',
        timeMax=end_time + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])


def description_of_event(user, room, event_input):
    return (
        f"Jméno/Name: {user.first_name} {user.surname}\n"
        f"Pokoj/Room: {room.door_number}\n"
        f"Číslo osob/Participants: {event_input.guests}\n"
        f"Účel/Purpose: {event_input.purpose}\n"
    )


def ready_event(calendar, event_input, user, room):
    return {
        "summary": calendar["event_name"],
        "description": description_of_event(user, room, event_input),
        "start": {
            "dateTime": event_input.start_datetime,
            "timeZone": "Europe/Vienna"
        },
        "end": {
            "dateTime": event_input.end_datetime,
            "timeZone": "Europe/Vienna"
        },
    }


def check_membership(services):
    for item in services:
        if "service" in item and "name" in item["service"] and item["service"]["name"] == "Základní členství":
            return True
    return False


def type_of_reservation(type_res: str) -> dict:
    result = {
        "Entire Space": lambda: {
            "calendar_id": "c_19586a3da50ca06566ef62012d6829ebf4e3026108212e9f9d0cc2fc6bc7c44a@group.calendar.google.com",
            "event_name": "Celý Prostor/Entire Space"
        },

        "Table Soccer": lambda: {
            "calendar_id": "c_f8a87bad9df63841a343835e6c559643835aa3c908302680324807b61dcb7e49@group.calendar.google.com",
            "event_name": "Stolní Fotbal/Table Soccer"
        },

        "Poker": lambda: {
            "calendar_id": "c_90c053583d4d2ae156551c6ecd311f87dad610a3272545c363879645f6968cef@group.calendar.google.com",
            "event_name": "Poker"
        },

        "Projector ": lambda: {
            "calendar_id": "c_4f3ccb9b25e3e37bc1dcea8784a8a11442d39e700809a12bee21bbeeb67af765@group.calendar.google.com",
            "event_name": "Projector"
        },

        "Pool": lambda: {
            "calendar_id": "c_8fc8c6760f7e32ed57785cf4739dc63e406b4a802aeec65ca0b1a3f56696263d@group.calendar.google.com",
            "event_name": "Kulečník/Pool"
        },

        "Study Room": lambda: {
            "calendar_id": "c_8f07a054dc4cd02f848491ffee9adb0302611811e711ffe921e4025d18d42ef2@group.calendar.google.com",
            "event_name": "Celá Klubová Studovna/Entire Club Study Room"
        },

        "Study Desk": lambda: {
            "calendar_id": "c_609bc4fdefe310e30dec02d90753f434d82cd738818dec679ad018d12731f97f@group.calendar.google.com",
            "event_name": "Studijní Stůl/Study Desk"
        },

        "Grill": lambda: {
            "calendar_id": "c_6cab3396f3e0d400d07904b08f427ff9c66b90b809488cfe6401a87891ab1cfd@group.calendar.google.com",
            "event_name": "Grill"
        },

    }.get(type_res, lambda: "primary")()

    return result
