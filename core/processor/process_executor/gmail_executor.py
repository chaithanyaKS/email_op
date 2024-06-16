import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from core.processor.action import Action, ActionType

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailProcessExecutor:
    def __init__(self) -> None:
        self._creds = None
        self._authenticate()

    def execute(self, actions: list[Action], msg_ids: list[str]):
        labels_to_add = []
        labels_to_remove = []
        for action in actions:
            if action.type == ActionType.MOVE_MESSAGE:
                labels_to_add.append(action.value.upper())
            elif action.type == ActionType.MARK_AS_READ:
                labels_to_remove.append("UNREAD")

        service = build("gmail", "v1", credentials=self._creds)
        bt = service.new_batch_http_request()
        for message_id in msg_ids:
            bt.add(
                service.users()
                .messages()
                .modify(
                    userId="me",
                    id=message_id,
                    body={
                        "addLabelIds": labels_to_add,
                        "removeLabelIds": labels_to_remove,
                    },
                )
            )
        bt.execute()

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
