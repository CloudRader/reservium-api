"""
This module defines an abstract base class AbstractEventService that work with Event.
Test variant
"""
import datetime as dt
from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Any

from schemas import EventInput, User, Room


class AbstractEventService(ABC):
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


class EventService(AbstractEventService):

    def post_event(self, event_input: EventInput, user: User, room: Room, creds, services) -> Any:
        found = False
        for item in services:
            if "service" in item and "name" in item["service"] and item["service"]["name"] == "Základní členství":
                found = True
                break

        if found == False:
            return {"message": "You are not member of the club!"}

        service = build("calendar", "v3", credentials=creds)

        calendar = self.type_of_reservation(event_input.reservation_type)

        check_collision = self.__get_events(service,
                                            self.__parse_datetime(event_input.start_datetime),
                                            self.__parse_datetime(event_input.end_datetime))

        if len(check_collision) > 0:
            return {"message": "There's already a reservation for that time"}

        description = (
            f"Jméno/Name: {user.first_name} {user.surname}\n"
            f"Pokoj/Room: {room.door_number}\n"
            f"Číslo osob/Participants: {event_input.guests}\n"
            f"Účel/Purpose: {event_input.purpose}\n"
        )

        event = {
            "summary": calendar["event_name"],
            "description": description,
            "start": {
                "dateTime": self.__parse_datetime(event_input.start_datetime),
                "timeZone": "Europe/Vienna"
            },
            "end": {
                "dateTime": self.__parse_datetime(event_input.end_datetime),
                "timeZone": "Europe/Vienna"
            },
        }

        event = service.events().insert(calendarId=calendar["calendar_id"], body=event).execute()

        print(f"Event created {event.get('htmlLink')}")

        return event

    @staticmethod
    def __get_events(service, start_time, end_time):
        # Call the Calendar API
        events_result = service.events().list(
            calendarId="c_19586a3da50ca06566ef62012d6829ebf4e3026108212e9f9d0cc2fc6bc7c44a@group.calendar.google.com",
            timeMin=start_time + 'Z',
            timeMax=end_time + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])

    @staticmethod
    def __parse_datetime(user_input):
        # Parse user-friendly datetime input in the format dd/mm/yyyy-hh/mm and convert to the required format
        parsed_dt = dt.datetime.strptime(user_input, '%d/%m/%Y-%H:%M')
        return parsed_dt.strftime('%Y-%m-%dT%H:%M:%S')

    def type_of_reservation(self, type: str) -> dict:
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

        }.get(type, lambda: "primary")()

        return result
