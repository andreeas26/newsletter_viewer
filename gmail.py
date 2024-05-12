import os.path
import base64
import pathlib as pt
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from data_types import EmailMessage
# If modifying these scopes, delete the file token.json.
_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

_GMAIL_PATH = pt.Path().cwd()/"gmail_authentication"

_CREDS_PATH = _GMAIL_PATH/"credentials.json"
_TOKEN_PATH = _GMAIL_PATH/"token.json"



class GmailEmail:
    def __init__(self, scopes: List[str] = _SCOPES, creds_path: str = _CREDS_PATH, token_path: str = _TOKEN_PATH) -> None:
        self.scopes = scopes
        self.creds_path = creds_path
        self.__token_path = token_path

        self.__creds = self.__authenticate()
        
    def __authenticate(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.__token_path):
            creds = Credentials.from_authorized_user_file(self.__token_path, self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_path, self.scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.__token_path, "w") as token:
                token.write(creds.to_json())

        return creds

    def list_labels(self) -> List[str] | None:
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """

        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=self.__creds)
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            if not labels:
                print("No labels found.")

            print("Labels:")
            for label in labels:
                print(label["id"], label["name"])
            
            return [label["name"] for label in labels]

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

    def list_messages(self, max_results: int = 2, label_ids: List[str] = ["UNREAD"]) -> List[EmailMessage] | None:
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail new messages.
        """
        emails = []
        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=self.__creds)
            results = service.users().messages().list(userId="me", maxResults=max_results, labelIds=label_ids, includeSpamTrash=False).execute()
            messages = results.get("messages", [])

            emails = []

            if not messages:
                print("No messages found.")
                return
            else:
                print(f"[INFO] Found {len(messages)} messages")
                # print(messages[0])
                # msg = service.users().messages().get(userId="me", id=messages[0]["id"]).execute()
                # print(type(msg))
                # for k, v in msg.items():
                #     print(k, type(v))

                for message in messages:
                    msg = service.users().messages().get(userId="me", id=message["id"]).execute()                
                    email_data = msg["payload"]["headers"]
                    current_email = EmailMessage(id=message["id"])
                    for values in email_data:
                        name = values["name"]
                        if name == "From":
                            from_name = values["value"]
                            current_email.sender = from_name
                            print(f"\tFrom: {from_name}")

                        if name == "Subject":
                            subject = values["value"]
                            current_email.subject = subject
                            print(f"\tSubject: {subject}")
                        
                        if name == "InternalDate":
                            date = values["value"]
                            # current_email.date = date
                            print(f"\tDate: {date}")

                    if "parts" in msg["payload"]:
                        for part in msg["payload"]["parts"]:
                            try:
                                data = part["body"]["data"]
                                byte_code = base64.urlsafe_b64decode(data)

                                text = byte_code.decode("utf-8")
                                print (f"\tMessage: {text[:200]}")
                                current_email.message = text

                            # mark the message as read (optional)
                            # msg = service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()                                                       
                            except BaseException as error:
                                pass
                    
                    emails.append(current_email)
                    print("-" * 100)
                
                print("\n\n")

                for email in emails:
                    print(email)      

                return emails      

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

def main():
    gmail = GmailEmail()
    gmail.list_labels()
    gmail.list_messages()


if __name__ == "__main__":
    main()
