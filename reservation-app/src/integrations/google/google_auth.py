"""API controllers for authorisation in google."""

import os.path

from core import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def auth_google(creds):
    """
    Authenticate and return Google credentials.

    This function handles the authentication for Google APIs. It checks for existing
    credentials in 'token.json'. If they are not present or invalid, it initiates the
    OAuth2 flow to obtain new credentials.

    :param creds: Initial credentials.

    :return: Authenticated Google credentials.
    """
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": settings.GOOGLE.CLIENT_ID,
                        "project_id": settings.GOOGLE.PROJECT_ID,
                        "auth_uri": settings.GOOGLE.AUTH_URI,
                        "token_uri": settings.GOOGLE.TOKEN_URI,
                        "auth_provider_x509_cert_url": settings.GOOGLE.AUTH_PROVIDER_X509_CERT_URL,
                        "client_secret": settings.GOOGLE.CLIENT_SECRET,
                        "redirect_uris": settings.GOOGLE.REDIRECT_URIS,
                    },
                },
                settings.GOOGLE.SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds
