"""
API controllers for authorisation in google.
"""
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from core import settings


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
            flow = InstalledAppFlow.from_client_config({
                "installed": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "project_id": settings.GOOGLE_PROJECT_ID,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": ["http://localhost"],
                }
            }, settings.GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds
