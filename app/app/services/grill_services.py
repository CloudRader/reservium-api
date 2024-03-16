"""
This module defines an abstract base class AbstractEventService that work with Event.
Test variant
"""
import datetime as dt
import pytz
from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Any
from services.utils import type_of_reservation, get_events, check_membership

from schemas import EventInput, User, Room


class AbstractGrillService(ABC):
    """
    This abstract class defines the interface for an event service.
    """

    @abstractmethod
    def post_event(self, event_input: EventInput, user: User, room: Room, creds, services) -> Any:
        """
        Post document in google calendar.
        :param event_input: EventThat me need to post.
        :param user:
        :param room:
        :param creds:
        :param services:
        """


class GrillService(AbstractGrillService):

    def post_event(self, event_input: EventInput, user: User, room: Room, creds, services) -> Any:

        service = build("calendar", "v3", credentials=creds)

        calendar = type_of_reservation(event_input.reservation_type)

        message = self.control_conditions_and_permissions(services, event_input, service, calendar)

        if message != "Access":
            return message

        description = (
            f"Pokoj/Room: {room.door_number}\n"
            f"Číslo osob/Participants: {event_input.guests}\n"
            f"Účel/Purpose: {event_input.purpose}\n"
        )

        event = {
            "summary": f"{user.first_name} {user.surname}",
            "description": description,
            "start": {
                "dateTime": event_input.start_datetime,
                "timeZone": "Europe/Vienna"
            },
            "end": {
                "dateTime": event_input.end_datetime,
                "timeZone": "Europe/Vienna"
            },
        }

        event = service.events().insert(calendarId=calendar["calendar_id"], body=event).execute()

        print(f"Event created {event.get('htmlLink')}")

        return event

    def control_conditions_and_permissions(self, services, event_input, service, calendar):
        # Check of the membership
        if not check_membership(services):
            return {"message": "You are not member of the club!"}

        start_datetime = dt.datetime.strptime(event_input.start_datetime, '%Y-%m-%dT%H:%M:%S')
        end_datetime = dt.datetime.strptime(event_input.end_datetime, '%Y-%m-%dT%H:%M:%S')

        # Check error reservation
        if start_datetime < dt.datetime.now():
            return {"message": "You can't make a reservation before the present time!"}

        # Check available reservation time
        if not self.__control_available_reservation_time(start_datetime, end_datetime):
            return {"message": "You can't reserve in this gap!"}

        # Check collision with other reservation
        check_collision = get_events(service,
                                     event_input.start_datetime,
                                     event_input.end_datetime, calendar)

        if not self.__check_collision_time(check_collision, start_datetime, end_datetime):
            return {"message": "There's already a reservation for that time."}

        # Reservation no more than 24 hours
        if not self.__dif_days_res(start_datetime, end_datetime):
            return {"message": "You can reserve on different day."}

        # Reservation in advance
        if not self.__control_res_in_advance(start_datetime):
            return {"message": "You have to make reservations 24 hours in advance!"}

        return "Access"

    @staticmethod
    def __dif_days_res(start_datetime, end_datetime):
        print(start_datetime.year)
        print(end_datetime.year)
        if start_datetime.year != end_datetime.year \
                or start_datetime.month != end_datetime.month \
                or start_datetime.day != end_datetime.day:
            return False
        return True

    @staticmethod
    def __control_res_in_advance(start_time):
        current_time = dt.datetime.now()

        time_difference = abs(start_time - current_time)

        if time_difference < dt.timedelta(hours=24):
            return False
        return True

    @staticmethod
    def __control_available_reservation_time(start_datetime, end_datetime):
        start_time = start_datetime.time()
        end_time = end_datetime.time()

        start_res_time = dt.datetime.strptime('08:00:00', '%H:%M:%S').time()
        end_res_time = dt.datetime.strptime('22:00:00', '%H:%M:%S').time()

        if start_time < start_res_time or end_time < start_res_time \
                or end_time > end_res_time:
            return False
        return True

    @staticmethod
    def __check_collision_time(check_collision, start_datetime, end_datetime):
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
