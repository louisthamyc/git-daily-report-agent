import base64
import os.path
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CREDENTIALS_FILE = os.path.join(
    PROJECT_DIR,
    "credentials",
    "credentials.json",
)

TOKEN_FILE = os.path.join(
    PROJECT_DIR,
    "credentials",
    "token.json",
)


def get_gmail_service():
    credentials = None

    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if not credentials or not credentials.valid:

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )

            credentials = flow.run_local_server(
                port=0
            )

        with open(TOKEN_FILE, "w") as token:
            token.write(credentials.to_json())

    return build(
        "gmail",
        "v1",
        credentials=credentials,
    )


def send_email(
    recipient,
    subject,
    html_content,
):
    service = get_gmail_service()

    message = MIMEText(
        html_content,
        "html",
        "utf-8",
    )

    message["to"] = recipient
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    body = {
        "raw": encoded_message
    }

    result = service.users().messages().send(
        userId="me",
        body=body,
    ).execute()

    return result
