"""
Utils for API.
"""
import httpx
from fastapi.responses import RedirectResponse


async def get_request(token: str, request: str):
    info_endpoint = "https://api.is.buk.cvut.cz/v1/" + request

    async with httpx.AsyncClient() as client:
        response = await client.get(info_endpoint, headers={"Authorization": f"Bearer {token}"})

        if response.status_code == 401:
            return RedirectResponse(url="https://10.0.52.106:8000/auth_is/login")

        response.raise_for_status()

        response_data = response.json()

    return response_data


class FastApiDocs:
    """Information for fastapi documentation."""
    NAME = "Reservation System of the Buben Club"
    DESCRIPTION = """Reservation System of the Buben Club API is a **REST API** that offers you an access to
    our application!"""
    VERSION = "1.0.0"
    AUTHORISATION_TAG = {
        "name": "users",
        "description": "Authorisation in IS.",
    }

    def get_tags_metadata(self):
        """Get tags metadata."""
        return [
            self.AUTHORISATION_TAG,
        ]


fastapi_docs = FastApiDocs()

# pylint: enable=too-few-public-methods
