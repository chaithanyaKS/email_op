import base64
import os.path
from typing import Protocol

from dateutil.parser import parse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core.models import Email

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
MULTIPART_MIME_TYPES = ["multipart/alternative", "multipart/mixed", "multipart/related"]


class Loader(Protocol):
    def load_data(self): ...


class GmailLoader:
    def __init__(self) -> None:
        self.email_data = []
        self._creds = None
        self._authenticate()

    def load_data(self, limit: int = 10):
        self._fetch_emails(limit)
        Email.objects.bulk_create(self._prepare_data_for_db())

    def _prepare_data_for_db(self):
        for data in self.email_data:
            yield Email(**data)

    def _callback(self, request_id, response, exception):
        if exception is not None:
            print("request_id: {}, exception: {}".format(request_id, str(exception)))
            pass
        else:
            email_data = self._process_data(response)
            self.email_data.append(email_data)

    def _authenticate(self):
        if os.path.exists("token.json"):
            self._creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self._creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self._creds.to_json())

    def _extract_body_from_multipart(self, payload: dict) -> str:
        for part in payload["parts"]:
            if part["mimeType"] == "text/html" or part["mimeType"] == "text/plain":
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode()
                return body
            else:
                return ""

        return ""

    def _process_data(self, payload: dict):
        msg_id = payload["id"]
        subject = None
        from_email = None
        received_at = ""
        body = None
        headers = payload["payload"]["headers"]
        for header in headers:
            if header["name"] == "Subject":
                subject = header["value"]
            elif header["name"] == "From":
                from_email = header["value"]
            elif header["name"] == "Date":
                received_at = header["value"]
        mimetype = payload["payload"]["mimeType"]
        if mimetype in MULTIPART_MIME_TYPES:
            body = self._extract_body_from_multipart(payload["payload"])
        else:
            body = payload["payload"]["body"]["data"]
            body = base64.urlsafe_b64decode(body).decode()

        return {
            "msg_id": msg_id,
            "subject": subject,
            "from_email": from_email,
            "received_at": parse(received_at),
            "message": body,
        }

    def _fetch_emails(self, limit: int):
        try:
            service = build("gmail", "v1", credentials=self._creds)

            messages_result = (
                service.users().messages().list(userId="me", maxResults=limit).execute()
            )
            messages = messages_result.get("messages", [])
            bt = service.new_batch_http_request(callback=self._callback)
            for msg in messages:
                msg = service.users().messages().get(userId="me", id=msg["id"])
                bt.add(msg)
            bt.execute()

        except HttpError as error:
            print(f"An error occurred: {error}")
