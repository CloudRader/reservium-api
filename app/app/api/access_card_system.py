"""
API controllers for authorisation in access card system.
"""
from typing import Any, Dict, Annotated
import requests
from fastapi import APIRouter, HTTPException, Depends, status

from services import AccessCardSystemService, EventService
from api import PermissionDeniedException
from schemas import VarSymbolCreateUpdate, VarSymbolDelete, Event, \
    ClubAccessSystemRequest
from core import settings
from .docs import fastapi_docs

router = APIRouter(
    prefix='/access_card_system',
    tags=[fastapi_docs.ACCESS_CARD_SYSTEM_TAG["name"]]
)


def send_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a JSON-formatted POST request to the dormitory access control API.

    :param data: Dictionary representing the request payload.

    :returns: Dictionary response parsed from the API’s JSON reply.
    :raises HTTPException: If the API returns a non-200 status code.
    """
    headers = {
        "Content-Type": "application/json",
        "Api-Key": settings.DORMITORY_ACCESS_SYSTEM_API_KEY
    }

    response = requests.post(
        settings.DORMITORY_ACCESS_SYSTEM_API_URL,
        json=data, headers=headers, timeout=5
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


@router.post("/external_authorize",
             responses={
                 **PermissionDeniedException.RESPONSE,
             },
             status_code=status.HTTP_201_CREATED,
             )
async def reservation_access_authorize(
        service: Annotated[AccessCardSystemService, Depends(AccessCardSystemService)],
        event_service: Annotated[EventService, Depends(EventService)],
        access_request: ClubAccessSystemRequest
) -> Any:
    """
    Endpoint for external access authorization.

    This endpoint receives an access request from the club access control system
    containing a user's UID, room ID, and device ID. It checks whether the user has
    a valid reservation and is authorized to access the specified room and device
    at the current time.

    :param service: AccessCardSystemService instance used for authorization logic.
    :param event_service: EventService for querying reservation data.
    :param access_request: Incoming request with UID, room ID, and device ID.

    :return: Boolean result indicating whether access is granted.
    """
    result = await service.reservation_access_authorize(event_service, access_request)
    return result


# Can be uncommented for testing dormitory card system
# Car symbol for testing: 2220015516
# @router.post("/add_var_symbol")
async def add_var_symbol(
        service: Annotated[AccessCardSystemService, Depends(AccessCardSystemService)],
        access_body: VarSymbolCreateUpdate
):
    """
    Add or update a variable symbol in the access group.

    :param service: AccessCardSystemService ser.
    :param access_body: Body for create or update var symbol in ACS.

    :returns: The result from the API.
    """
    data = await service.add_var_symbol(access_body)
    return send_request(data)


# @router.delete("/del_var_symbol")
async def del_var_symbol(
        service: Annotated[AccessCardSystemService, Depends(AccessCardSystemService)],
        access_body: VarSymbolDelete,
):
    """
    Delete a variable symbol from the access group.

    :param service: AccessCardSystemService ser.
    :param access_body: Body for delete var symbol in ACS.

    :returns: The result from the API.
    """
    data = await service.del_var_symbol(access_body)
    return send_request(data)


# @router.get("/get_groups_for_use")
async def get_groups_for_use(
        service: Annotated[AccessCardSystemService, Depends(AccessCardSystemService)],
):
    """
    Get the list of available groups for the API key.

    :param service: AccessCardSystemService ser.
    :returns: The result from the API.
    """
    data = await service.get_groups_for_use()
    return send_request(data)


# @router.get("/get_access_var_symbol")
async def get_access_var_symbol(
        service: Annotated[AccessCardSystemService, Depends(AccessCardSystemService)],
        var_symbol: str,
):
    """
    Get the list of groups for a given variable symbol.

    :param service: AccessCardSystemService ser.
    :param var_symbol: The var symbol that identifies the user in ISKAM.

    :returns: The result from the API.
    """
    data = await service.get_access_var_symbol(var_symbol)
    return send_request(data)


# @router.get("/get_access_group")
async def get_access_group(
        service: Annotated[AccessCardSystemService, Depends(AccessCardSystemService)],
        group: str,
):
    """
    Get the list of variable symbols for a given group.

    :param service: AccessCardSystemService ser.
    :param group: The group of the reader in the ACS.

    :returns: The result from the API.
    """
    data = await service.get_access_group(group)
    return send_request(data)


async def add_or_update_access_to_reservation_areas(
        service_event: Annotated[EventService, Depends(EventService)],
        event: Event,
) -> Any:
    """
    Add or update access control entries for a reservation event.

    :param service_event: Event service to resolve event relationships.
    :param event: The Event object in db.

    :return: A success message indicating that the access entries were processed.
    """
    reservation_service = await service_event.get_reservation_service_of_this_event(
        event
    )
    user = await service_event.get_user_of_this_event(event)

    valid_from = event.start_datetime.strftime("%Y-%m-%d")  # for now
    valid_to = event.end_datetime.strftime("%Y-%m-%d")
    var_symbol = "2220015516"  # in the future will be user.var_symbol

    data_list: list = []

    if not user.active_member:
        if reservation_service.access_group:
            access_body = {
                "funkce": "AddVarSymbolSkupina",
                "varsymbol": var_symbol,
                "skupina": reservation_service.access_group,
                "platnostod": valid_from,
                "platnostdo": valid_to
            }
            data_list.append(access_body)

        for mini_service in reservation_service.mini_services:
            if mini_service.access_group:
                access_body = {
                    "funkce": "AddVarSymbolSkupina",
                    "varsymbol": var_symbol,
                    "skupina": mini_service.access_group,
                    "platnostod": valid_from,
                    "platnostdo": valid_to
                }
                data_list.append(access_body)

        for data in data_list:
            send_request(data)

    return {"message": "Successful updating access"}


async def delete_access_to_reservation_areas(
        service_event: Annotated[EventService, Depends(EventService)],
        event: Event,
) -> Any:
    """
    Delete access control entries for a reservation event.

    :param service_event: Event service to resolve event relationships.
    :param event: The Event object in db.

    :return: A success message indicating that the access entries were processed.
    """
    reservation_service = await service_event.get_reservation_service_of_this_event(
        event
    )
    user = await service_event.get_user_of_this_event(event)

    var_symbol = "2220015516"  # in the future will be user.var_symbol

    data_list: list = []

    if not user.active_member:
        if reservation_service.access_group:
            access_body = {
                "funkce": "DelVarSymbolSkupina",
                "varsymbol": var_symbol,
                "skupina": reservation_service.access_group,
            }
            data_list.append(access_body)

        for mini_service in reservation_service.mini_services:
            if mini_service.access_group:
                access_body = {
                    "funkce": "DelVarSymbolSkupina",
                    "varsymbol": var_symbol,
                    "skupina": reservation_service.access_group,
                }
                data_list.append(access_body)

        for data in data_list:
            send_request(data)

    return {"message": "Successful updating access"}
