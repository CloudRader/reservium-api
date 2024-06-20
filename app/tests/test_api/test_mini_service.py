"""
Module for testing mini services api
"""
from uuid import UUID
import json

import pytest
from httpx import Response
from starlette.testclient import TestClient
from schemas import MiniService


# pylint: disable=redefined-outer-name
# reason: using fixtures as variables is a standard for pytest


def get_answer_from_create_response(response: Response) -> dict:
    """
    Get answer from request response.
    """
    return json.loads(response.text)


@pytest.fixture(scope="module")
def mini_service_content() -> dict:
    """
    Return mini service content for request.
    """
    return {
        "service_alias": "stud",
        "name": "3d printer",
    }


@pytest.fixture(scope="module")
def mini_service_update_content() -> dict:
    """
    Return mini service update content for request.
    """
    return {
        "service_alias": "klub",
    }


def create_mini_service(client: TestClient,
                        mini_service_content, username):
    """
    Create mini service and check if correct answer was sent.
    """
    url = f"/mini_services/create_mini_service?username={username}"
    response_create = client.post(
        url,
        json=mini_service_content
    )
    assert response_create.status_code == 201
    answer = get_answer_from_create_response(response_create)
    assert answer is not None
    assert answer["uuid"] is not None
    return answer["uuid"]


def get_mini_service(
        client: TestClient, uuid,
) -> MiniService:
    """
    Get calendar and check all parameters are as expected.
    """
    url = f"/mini_services/{uuid}"
    response_get = client.get(url)
    assert response_get.status_code == 200
    mini_service = MiniService(**response_get.json())
    assert mini_service.uuid == UUID(uuid)
    assert mini_service.service_alias == "stud"
    return mini_service


def get_mini_services_by_alias(
        client: TestClient, alias,
) -> MiniService:
    """
    Get calendar and check all parameters are as expected.
    """
    url = f"/mini_services/alias/{alias}"
    response_get = client.get(url)
    assert response_get.status_code == 200
    data = json.loads(response_get.text)
    mini_service = MiniService(**data[0])
    assert mini_service.name == "3d printer"
    return mini_service


def test_create_and_get_mini_service(
        client: TestClient, mini_service_content,
        create_user_manager_stud
):
    """
    Test create and get calendar.
    """
    uuid = create_mini_service(client, mini_service_content,
                               create_user_manager_stud.username)
    get_mini_service(client, uuid)


def test_get_all_mini_services(client: TestClient):
    """
    Test get all mini services.
    """
    response = client.get("/mini_services")
    assert response.status_code == 200


def test_delete_mini_service(
        client: TestClient,
        create_user_manager_stud
):
    """
    Test delete mini service.
    """
    mini_service = get_mini_services_by_alias(client, "stud")
    url = f"/mini_services/{mini_service.uuid}" \
          f"?username={create_user_manager_stud.username}"
    response = client.delete(url)
    deleted_mini_service = MiniService(**response.json())
    assert response.status_code == 200
    assert deleted_mini_service.uuid == \
           mini_service.uuid


def test_update_mini_service(
        client: TestClient,
        mini_service_content,
        create_user_manager_stud,
        mini_service_update_content
):
    """
    Test update mini services.
    """
    uuid = create_mini_service(client, mini_service_content,
                               create_user_manager_stud.username)
    mini_service = get_mini_service(client, uuid)
    url = f"/mini_services/{uuid}" \
          f"?username={create_user_manager_stud.username}"
    response = client.put(
        url,
        json=mini_service_update_content
    )
    updated_mini_service = MiniService(**response.json())
    assert response.status_code == 200
    assert updated_mini_service.service_alias != \
           mini_service.service_alias
    assert updated_mini_service.service_alias == \
           mini_service_update_content["service_alias"]
