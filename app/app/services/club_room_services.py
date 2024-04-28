"""
This module defines an abstract base class AbstractClubRoomService that work with Event.
Test variant
"""
from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Any
from services.utils import type_of_reservation, get_events, control_conditions_and_permissions
from schemas import EventInput, UserIS, Room


class AbstractClubRoomService(ABC):
    """
    This abstract class defines the interface for an event service.
    """

    @abstractmethod
    def post_event(self, event_input: EventInput, user: UserIS, room: Room, creds, services) -> Any:
        """
        Post document in google calendar.
        :param event_input: EventThat me need to post.
        :param user:
        :param room:
        :param creds:
        :param services:
        """


class ClubRoomService(AbstractClubRoomService):

    def post_event(self, event_input: EventInput, user: UserIS, room: Room, creds, services) -> Any:

        service = build("calendar", "v3", credentials=creds)

        calendar = type_of_reservation(event_input.reservation_type)

        if calendar["event_name"] == "Study Room":
            message = control_conditions_and_permissions(services, event_input, service, calendar)
        else:
            calendar_study_room = type_of_reservation("Study Room")
            message = self.__control_conditions_and_permissions_study_desk(services, event_input,
                                                                           service, calendar, calendar_study_room)

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

    @staticmethod
    def __control_conditions_and_permissions_study_desk(services, event_input,
                                                        service, calendar, calendar_study_room):
        message = control_conditions_and_permissions(services, event_input, service, calendar_study_room)
        if message != "Access":
            return message

        # How many reservations for the study room at this time
        check_collision = get_events(service,
                                     event_input.start_datetime,
                                     event_input.end_datetime, calendar)

        if len(check_collision) > 10:
            return {"message": "There are no available seats in the study room."}

        return "Access"