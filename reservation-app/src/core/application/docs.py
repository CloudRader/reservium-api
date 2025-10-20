"""Package for API Documentation."""

from core.config import settings


class FastApiDocs:
    """Information for fastapi documentation."""

    NAME = f"Reservation System of the {settings.ORGANIZATION_NAME}"
    DESCRIPTION = (
        f"Reservation System of the {settings.ORGANIZATION_NAME} API is "
        "a REST API that offers you an access to application!\n\n"
        "## Basic rules to follow\n"
        "- `POST`\n\n"
        "  - Creates a record in collection\n\n"
        "  - Calls an action\n"
        "- `PUT`\n\n"
        "  - Updates object\n"
        "- `DELETE`\n\n"
        "  - Delete object\n\n"
        "## Authentication\n"
        "The application uses OAuth2 for authentication.\n\n"
        "### Supported grant types:\n"
        "- authorization_code"
    )
    VERSION = "2.0.0"
    AUTHORISATION_TAG = {
        "name": "auth",
        "description": "Authorisation in IS.",
    }
    USER_TAG = {
        "name": "users",
        "description": "Operations with users.",
    }
    RESERVATION_SERVICE_TAG = {
        "name": "reservation services",
        "description": "Operations with reservation services.",
    }
    CALENDAR_TAG = {
        "name": "calendars",
        "description": "Operations with calendars.",
    }
    MINI_SERVICE_TAG = {
        "name": "mini services",
        "description": "Operations with mini services.",
    }
    EVENT_TAG = {
        "name": "events",
        "description": "Operations with events.",
    }
    EMAIL_TAG = {
        "name": "emails",
        "description": "Operations with emails.",
    }
    ACCESS_CARD_SYSTEM_TAG = {
        "name": "access card system",
        "description": "Operations with access card system.",
    }

    def get_tags_metadata(self):
        """Get tags metadata."""
        return [
            self.AUTHORISATION_TAG,
            self.USER_TAG,
            self.RESERVATION_SERVICE_TAG,
            self.CALENDAR_TAG,
            self.MINI_SERVICE_TAG,
            self.EVENT_TAG,
            self.EMAIL_TAG,
            self.ACCESS_CARD_SYSTEM_TAG,
        ]


fastapi_docs = FastApiDocs()
