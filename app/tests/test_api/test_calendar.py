"""
Module for testing calendar api
"""
# Commented this tests, because add check existing calendar on Google.
# It broke this tests, I don't want communication with Google from tests modules.
# Before that tests worked excellent

# import json
#
# import pytest
# from httpx import Response
# from starlette.testclient import TestClient
# from schemas import Calendar, Rules
#
#
# # pylint: disable=redefined-outer-name
# # reason: using fixtures as variables is a standard for pytest
#
#
# def get_answer_from_create_response(response: Response) -> dict:
#     """
#     Get answer from request response.
#     """
#     return json.loads(response.text)
#
#
# @pytest.fixture(scope="module")
# def calendar_content(rules_json_club_member) -> dict:
#     """
#     Return calendar content for request.
#     """
#     return {
#         "calendar_id": "f62012d6829ebf4e30261",
#         "service_alias": "stud",
#         "reservation_type": "Study Room",
#         "event_name": "Studovna/Study Room",
#         "max_people": 10,
#         "collision_with_itself": False,
#         "collision_with_calendar": [],
#         "club_member_rules": rules_json_club_member,
#         "active_member_rules": rules_json_club_member,
#         "manager_rules": rules_json_club_member
#     }
#
#
# @pytest.fixture(scope="module")
# def calendar_update_content() -> dict:
#     """
#     Return calendar update content for request.
#     """
#     return {
#         "max_people": 5,
#     }
#
#
# def create_calendar(client: TestClient, calendar_content, username):
#     """
#     Create calendar and check if correct answer was sent.
#     """
#     url = f"/calendars/create_calendar?username={username}"
#     response_create = client.post(
#         url,
#         json=calendar_content
#     )
#     assert response_create.status_code == 201
#     answer = get_answer_from_create_response(response_create)
#     assert answer is not None
#     assert answer["calendar_id"] is not None
#     assert answer["calendar_id"] == calendar_content["calendar_id"]
#     return answer["calendar_id"]
#
#
# def get_calendar(
#         client: TestClient, calendar_id, calendar_content
# ) -> Calendar:
#     """
#     Get calendar and check all parameters are as expected.
#     """
#     url = f"/calendars/{calendar_id}"
#     response_get = client.get(url)
#     assert response_get.status_code == 200
#     calendar = Calendar(**response_get.json())
#     rules = Rules(**calendar_content["club_member_rules"])
#     assert calendar.calendar_id == "f62012d6829ebf4e30261"
#     assert calendar.service_alias == "stud"
#     assert calendar.reservation_type == "Study Room"
#     assert calendar.event_name == "Studovna/Study Room"
#     assert not calendar.collision_with_itself
#     assert calendar.manager_rules == rules
#     return calendar
#
#
# def test_create_and_get_calendar(
#         client: TestClient, calendar_content,
#         create_user_manager_stud
# ):
#     """
#     Test create and get calendar.
#     """
#     calendar_id = create_calendar(client, calendar_content,
#                                   create_user_manager_stud.username)
#     get_calendar(client, calendar_id, calendar_content)
#
#
# def test_get_all_calendars(client: TestClient):
#     """
#     Test get all calendars.
#     """
#     response = client.get("/calendars")
#     assert response.status_code == 200
#
#
# def test_update_calendar(
#         client: TestClient,
#         calendar_content,
#         create_user_manager_stud,
#         calendar_update_content
# ):
#     """
#     Test update calendar.
#     """
#     calendar = get_calendar(client, "f62012d6829ebf4e30261", calendar_content)
#     url = f"/calendars/f62012d6829ebf4e30261" \
#           f"?username={create_user_manager_stud.username}"
#     response = client.put(
#         url,
#         json=calendar_update_content
#     )
#     updated_calendar = Calendar(**response.json())
#     assert response.status_code == 200
#     assert updated_calendar.max_people != calendar.max_people
#     assert updated_calendar.max_people == \
#            calendar_update_content["max_people"]
#
#
# def test_delete_calendar(
#         client: TestClient,
#         calendar_content,
#         create_user_manager_stud
# ):
#     """
#     Test delete calendar.
#     """
#     calendar = get_calendar(client, "f62012d6829ebf4e30261", calendar_content)
#     url = f"/calendars/{calendar.calendar_id}" \
#           f"?username={create_user_manager_stud.username}"
#     response = client.delete(url)
#     deleted_calendar = Calendar(**response.json())
#     assert response.status_code == 200
#     assert deleted_calendar.calendar_id == \
#            calendar.calendar_id
