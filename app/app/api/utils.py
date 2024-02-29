"""
Utils for API.
"""


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
