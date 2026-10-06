import os
import io
from googleapiclient.http import (
    MediaIoBaseUpload,
    MediaIoBaseDownload
)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]


def get_drive_service():

    creds = None

    if os.path.exists("token.json"):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(
                Request()
            )

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        with open(
            "token.json",
            "w"
        ) as token:

            token.write(
                creds.to_json()
            )

    from googleapiclient.discovery import build

    service = build(
        "drive",
        "v3",
        credentials=creds
    )

    return service

def upload_memory(
    service,
    file_bytes,
    file_name,
    mime_type
):

    results = service.files().list(
        q="name='SAFAR Memories' "
        "and mimeType='application/vnd.google-apps.folder' "
        "and trashed=false",
        spaces="drive",
        fields="files(id, name)"
    ).execute()

    folders = results.get(
        "files",
        []
    )

    if folders:

        folder_id = folders[0]["id"]

    else:

        folder_metadata = {
            "name": "SAFAR Memories",
            "mimeType": "application/vnd.google-apps.folder"
        }

        folder = service.files().create(
            body=folder_metadata,
            fields="id"
        ).execute()

        folder_id = folder["id"]

    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }

    media = MediaIoBaseUpload(
        io.BytesIO(file_bytes),
        mimetype=mime_type,
        resumable=True
    )

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name"
    ).execute()

    return uploaded_file

def get_safar_memories(service):

    results = service.files().list(
        q="name='SAFAR Memories' "
        "and mimeType='application/vnd.google-apps.folder' "
        "and trashed=false",
        spaces="drive",
        fields="files(id, name)"
    ).execute()

    folders = results.get(
        "files",
        []
    )

    if not folders:

        return []

    folder_id = folders[0]["id"]

    memories = service.files().list(
        q=f"'{folder_id}' in parents "
        "and trashed=false",
        spaces="drive",
        fields="files(id, name, mimeType)",
        orderBy="createdTime desc"
    ).execute()

    return memories.get(
        "files",
        []
    )


def get_memory_bytes(
    service,
    file_id
):

    file_data = io.BytesIO()

    request = service.files().get_media(
        fileId=file_id
    )

    downloader = MediaIoBaseDownload(
        file_data,
        request
    )

    done = False

    while not done:

        status, done = downloader.next_chunk()

    file_data.seek(0)

    return file_data.read()

def delete_memory(
    service,
    file_id
):

    service.files().update(
        fileId=file_id,
        body={
            "trashed": True
        }
    ).execute()