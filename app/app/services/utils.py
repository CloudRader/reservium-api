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
