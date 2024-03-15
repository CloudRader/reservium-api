"""
Utils for API.
"""
import httpx


def read_token_from_file(file_path="token.txt"):
    try:
        with open(file_path, "r") as token_file:
            token = token_file.read().strip()
            return token
    except FileNotFoundError:
        print(f"Token file '{file_path}' not found.")
        return None


async def get_request(token: str, request: str):
    info_endpoint = "https://api.is.buk.cvut.cz/v1" + request

    async with httpx.AsyncClient() as client:
        response = await client.get(info_endpoint, headers={"Authorization": f"Bearer {token}"})
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
